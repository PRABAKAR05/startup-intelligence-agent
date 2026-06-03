import time
import re
from google import genai
import config
from config import API_KEYS, logger

class DailyQuotaExhaustedError(Exception):
    pass

# Simple rate limiter: enforce a minimum interval between calls.
# Free-tier limit observed: 5 requests per minute per model -> 12s interval.
_last_call_ts = 0.0
_min_interval_seconds = 12.0

_current_key_idx = 0
if not API_KEYS:
    raise ValueError("No GEMINI API keys provided")
    
client = genai.Client(api_key=API_KEYS[_current_key_idx])

def _extract_retry_seconds_from_err(exc_text: str) -> int:
    m = re.search(r"retryDelay':\s*'(\d+)s'", exc_text)
    if m:
        return int(m.group(1))
    m2 = re.search(r'retryDelay"\s*:\s*"(\d+)s"', exc_text)
    if m2:
        return int(m2.group(1))
    # Fallback to common Retry-After header or policy
    return 60

def generate_content_with_rate_limit(model: str, contents: str, max_attempts: int = 5, **kwargs):
    global client, _current_key_idx, _last_call_ts
    """
    Call Gemini with simple client-side throttling and robust retries on 429.
    - Enforces a minimum interval between calls (_min_interval_seconds).
    - On 429/RESOURCE_EXHAUSTED, parses suggested retry delay and applies
      exponential backoff across attempts.
    - Raises the last exception if retries are exhausted.
    """
    attempt = 0
    last_exc = None

    while attempt < max_attempts:
        # Throttle to respect min interval
        if getattr(config, 'DAILY_QUOTA_EXHAUSTED', False):
            raise DailyQuotaExhaustedError("Daily API quota already exhausted")
            
        now = time.time()
        elapsed = now - _last_call_ts
        if elapsed < _min_interval_seconds:
            sleep_for = _min_interval_seconds - elapsed
            logger.info(f"Throttling Gemini calls: sleeping {sleep_for:.1f}s to respect rate limit")
            time.sleep(sleep_for)

        try:
            resp = client.models.generate_content(model=model, contents=contents, **kwargs)
            _last_call_ts = time.time()
            return resp

        except Exception as e:
            last_exc = e
            err_text = str(e)
            attempt += 1

            # If it's a 429 / RESOURCE_EXHAUSTED, respect server RetryInfo when present
            if 'RESOURCE_EXHAUSTED' in err_text or '429' in err_text:
                if 'GenerateRequestsPerDay' in err_text or 'RequestsPerDay' in err_text:
                    logger.warning(f"Daily API quota exhausted for key index {_current_key_idx}.")
                    _current_key_idx += 1
                    
                    if _current_key_idx < len(API_KEYS):
                        logger.info(f"Switching to backup API key {_current_key_idx + 1} of {len(API_KEYS)}")
                        client = genai.Client(api_key=API_KEYS[_current_key_idx])
                        continue # Retry immediately with the new key!
                    else:
                        logger.error("All available API keys exhausted. Cannot continue.")
                        config.DAILY_QUOTA_EXHAUSTED = True
                        raise DailyQuotaExhaustedError("All API keys exhausted")
                    
                try:
                    retry_seconds = _extract_retry_seconds_from_err(err_text)
                except Exception:
                    retry_seconds = None

                # Compute backoff: prefer server-suggested retry, otherwise exponential
                if retry_seconds and retry_seconds > 0:
                    backoff = min(retry_seconds, 300)
                else:
                    backoff = min(2 ** attempt, 300)

                logger.warning(
                    f"Gemini returned 429 (attempt {attempt}/{max_attempts}); sleeping {backoff}s then retrying"
                )
                time.sleep(backoff)
                continue

            # Non-429 errors should not be retried here
            logger.exception("Gemini call failed with non-429 error")
            raise

    # Exhausted retries
    logger.error("Retry after Gemini failures exhausted")
    if last_exc:
        raise last_exc
    raise RuntimeError("generate_content_with_rate_limit failed without exception")
