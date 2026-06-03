import json
import google.generativeai as genai
from config import GEMINI_API_KEY, logger
from tenacity import retry, stop_after_attempt, wait_exponential

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro')

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def extract_hiring(article_content, article_url, article_title, pub_date):
    prompt = f"""
    You are an AI trained to extract startup hiring news.
    Analyze the following article and determine if it contains announcements of a startup hiring (e.g., hiring drives, team expansion, opening new roles, mass hiring).
    If it DOES NOT contain hiring news, return {{"is_hiring_news": false}}.
    If it DOES contain hiring news, extract the following information and return it strictly as a JSON object:
    - is_hiring_news: true
    - startup_name
    - company_description
    - open_roles (list of strings, e.g., ["Software Engineer", "Product Manager"])
    - required_experience (string, e.g., "0-2 years", "Senior", "Any")
    - location (string)
    - remote_status (string: "Remote", "Hybrid", "Onsite", "Unknown")
    - founders (list of strings)

    Article Title: {article_title}
    Article Content: {article_content[:3000]} # Truncated for token limits
    
    Output JSON ONLY. Do not include markdown blocks.
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        data = json.loads(text)
        if data.get("is_hiring_news"):
            data["article_url"] = article_url
            data["publication_date"] = pub_date
            # Attempt to split roles to fresher/internship for later scoring if not specified
            return data
        return None
    except Exception as e:
        logger.error(f"Error extracting hiring news from {article_url}: {e}")
        return None
