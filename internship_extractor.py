import json
from google import genai
from config import GEMINI_API_KEY, logger
from tenacity import retry, stop_after_attempt, wait_exponential
from ai_client import generate_content_with_rate_limit

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=10, max=60))
def extract_internships_freshers(article_content, article_url, article_title, pub_date):
    prompt = f"""
    You are an AI trained to extract startup internship and fresher job opportunities.
    Analyze the following article and determine if it contains specific announcements about internships or entry-level/fresher jobs (0-2 years experience).
    If it DOES NOT contain such news, return {{"has_opportunities": false}}.
    If it DOES contain such news, extract the information and return strictly as a JSON object:
    - has_opportunities: true
    - startup_name
    - internships (list of objects with keys: role, stipend (if mentioned), location, remote_status)
    - fresher_jobs (list of objects with keys: role, experience_required, salary (if mentioned), location, remote_status)

    Article Title: {article_title}
    Article Content: {article_content[:3000]} # Truncated for token limits
    
    Output JSON ONLY. Do not include markdown blocks.
    """
    try:
        response = generate_content_with_rate_limit(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        data = json.loads(text)
        if data.get("has_opportunities"):
            data["article_url"] = article_url
            data["publication_date"] = pub_date
            return data
        return None
    except Exception as e:
        logger.error(f"Error extracting internships/freshers from {article_url}: {e}")
        return None
