import time
import re
from google import genai
from config import GEMINI_API_KEY, logger

# Simple rate limiter: enforce a minimum interval between calls.
# Free-tier limit observed: 5 requests per minute per model -> 12s interval.
_last_call_ts = 0.0
_min_interval_seconds = 12.0

client = genai.Client(api_key=GEMINI_API_KEY)

def _extract_retry_seconds_from_err(exc_text: str) -> int:
    m = re.search(r"retryDelay':\s*'(\d+)s'", exc_text)
    if m:
        return int(m.group(1))
    m2 = re.search(r'retryDelay"\s*:\s*"(\d+)s"', exc_text)
    if m2:
        return int(m2.group(1))
    # Fallback to common Retry-After header or policy
    return 60

def generate_content_with_rate_limit(model: str, contents: str, **kwargs):
    global _last_call_ts
    # Throttle to respect min interval
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
        # Attempt to parse RetryInfo from error message and wait
        try:
            err_text = str(e)
            if 'RESOURCE_EXHAUSTED' in err_text or '429' in err_text:
                retry_seconds = _extract_retry_seconds_from_err(err_text)
                logger.warning(f"Gemini returned 429; sleeping for {retry_seconds}s then retrying")
                time.sleep(retry_seconds)
                resp = client.models.generate_content(model=model, contents=contents, **kwargs)
                _last_call_ts = time.time()
                return resp
        except Exception:
            logger.exception("Retry after 429 failed")

        raise
