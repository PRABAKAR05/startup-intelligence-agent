# Indian Startup Funding & Hiring Intelligence Agent

A production-ready AI agent that automates the extraction, classification, and reporting of startup funding and hiring news in India.

## Features

- **Automated Scraping**: Daily fetching of news from major Indian startup portals.
- **AI-Powered Extraction**: Uses Google Gemini to intelligently parse unstructured articles into structured JSON data.
- **Categorization**: Separates funding news, hiring team expansions, internships, and fresher roles.
- **Founder Enrichment**: Uses web searches to find founder profiles and titles.
- **Placement Scoring**: Generates a custom 0-100 Placement Score based on funding, open roles, remote-friendliness, and internships to highlight the best startups for job seekers.
- **Comprehensive Reporting**: Generates a beautiful HTML email and exports data to CSV/XLSX (`hot_startups.csv`).
- **Fully Automated**: Runs daily at 7:00 AM IST via GitHub Actions.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd startup-intelligence-agent
```

### 2. Install Dependencies
Requires Python 3.12+
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the `.env.example` to `.env` and fill in your details:
```bash
cp .env.example .env
```
- `GEMINI_API_KEY`: Get from Google AI Studio.
- `EMAIL_ADDRESS`: Your Gmail address.
- `EMAIL_PASSWORD`: An App Password generated from your Google Account settings (do not use your regular password).
- `RECIPIENT_EMAIL`: Where you want to receive the daily reports.

### 4. Run Locally
```bash
python main.py
```
This will generate reports in the `reports/` folder, update `data/history.csv`, and send you an email.

## GitHub Actions Deployment

The agent is pre-configured to run every day at 7:00 AM IST.
To deploy:
1. Push this code to a GitHub repository.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add the following repository secrets:
   - `GEMINI_API_KEY`
   - `EMAIL_ADDRESS`
   - `EMAIL_PASSWORD`
   - `RECIPIENT_EMAIL`
4. Go to **Settings > Actions > General > Workflow permissions** and ensure it is set to **Read and write permissions** (so the bot can update `history.csv`).

## Data Structure
- `data/history.csv`: Keeps track of processed URLs to prevent duplicate reporting.
- `reports/`: Contains the generated daily HTML, CSV, and XLSX files.
