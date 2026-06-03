import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- API Keys & Credentials ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# --- Directories & Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

HISTORY_FILE = os.path.join(DATA_DIR, "history.csv")
HTML_REPORT_FILE = os.path.join(REPORTS_DIR, "daily_report.html")
CSV_REPORT_FILE = os.path.join(REPORTS_DIR, "daily_report.csv")
XLSX_REPORT_FILE = os.path.join(REPORTS_DIR, "daily_report.xlsx")
HOT_STARTUPS_FILE = os.path.join(REPORTS_DIR, "hot_startups.csv")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# --- Logging Configuration ---
log_filename = os.path.join(LOGS_DIR, f"agent_run_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("StartupIntelligence")

# --- News Sources ---
RSS_FEEDS = [
    "https://yourstory.com/feed",
    "https://inc42.com/feed/",
    "https://entrackr.com/feed/",
    "https://techcircle.in/feed",
    "https://www.vccircle.com/feed",
    "https://startupnews.fyi/feed/"
]

# Note: Some sources might not have RSS or easily scrapable static pages,
# they might require specific scraping logic in scraper.py.
