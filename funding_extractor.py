import json
from google import genai
from config import GEMINI_API_KEY, logger
from tenacity import retry, stop_after_attempt, wait_exponential
from ai_client import generate_content_with_rate_limit

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=10, max=60))
def extract_funding(article_content, article_url, article_title, pub_date):
    prompt = f"""
    You are an AI trained to extract startup funding news.
    Analyze the following article and determine if it contains an announcement of a startup raising funding (e.g., Seed, Pre-seed, Angel, Series A/B/C, Debt, Venture, Strategic).
    If it DOES NOT contain funding news, return {{"is_funding_news": false}}.
    If it DOES contain funding news, extract the following information and return it strictly as a JSON object:
    - is_funding_news: true
    - startup_name
    - industry
    - description (two-line description)
    - headquarters
    - funding_stage
    - funding_amount (include currency symbol or name if available)
    - currency
    - lead_investor
    - all_investors (list of strings)
    - founders (list of strings)
    - likely_hiring_soon (YES or NO, based on if they mention team expansion, hiring, scaling up, or just raised a significant round)
    
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
        if data.get("is_funding_news"):
            data["article_url"] = article_url
            data["publication_date"] = pub_date
            return data
        return None
    except Exception as e:
        logger.error(f"Error extracting funding from {article_url}: {e}")
        return None
