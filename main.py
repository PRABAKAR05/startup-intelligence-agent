import os
import pandas as pd
from datetime import datetime
from config import HISTORY_FILE, logger
from scraper import scrape_articles
from funding_extractor import extract_funding
from hiring_extractor import extract_hiring
from internship_extractor import extract_internships_freshers
from founder_enrichment import enrich_founders
from scoring import score_startups
from report_generator import generate_reports
from email_sender import send_email

def load_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE)['article_url'].tolist()
    return []

def update_history(processed_articles):
    if not processed_articles:
        return
        
    new_data = pd.DataFrame([{
        'startup_name': a.get('startup_name', 'Unknown'),
        'article_url': a.get('article_url', ''),
        'funding_amount': a.get('funding_amount', ''),
        'investors': ", ".join(a.get('all_investors', [])),
        'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    } for a in processed_articles])
    
    if os.path.exists(HISTORY_FILE):
        existing = pd.read_csv(HISTORY_FILE)
        updated = pd.concat([existing, new_data], ignore_index=True)
    else:
        updated = new_data
        
    updated.to_csv(HISTORY_FILE, index=False)
    logger.info(f"Updated history.csv with {len(new_data)} new records.")

def main():
    logger.info("Starting Daily Startup Intelligence Agent Run")
    
    history_urls = load_history()
    articles = scrape_articles()
    
    startups = {}
    processed = []
    
    for article in articles:
        if article['url'] in history_urls:
            continue
            
        logger.info(f"Processing article: {article['title']}")
        
        # We need to hit Gemini for each category if it might contain it.
        # To save tokens, one could combine prompts, but separation is cleaner.
        
        funding_data = extract_funding(article['content'], article['url'], article['title'], article['published_date'])
        hiring_data = extract_hiring(article['content'], article['url'], article['title'], article['published_date'])
        intern_fresh_data = extract_internships_freshers(article['content'], article['url'], article['title'], article['published_date'])
        
        # Merge data by startup name
        startup_name = None
        if funding_data:
            startup_name = funding_data['startup_name']
        elif hiring_data:
            startup_name = hiring_data['startup_name']
        elif intern_fresh_data:
            startup_name = intern_fresh_data['startup_name']
            
        if not startup_name:
            continue
            
        if startup_name not in startups:
            startups[startup_name] = {'startup_name': startup_name}
            
        sd = startups[startup_name]
        
        if funding_data:
            sd['recent_funding'] = True
            sd.update(funding_data)
            processed.append(funding_data)
            
        if hiring_data:
            sd['open_roles'] = sd.get('open_roles', []) + hiring_data.get('open_roles', [])
            if not sd.get('remote_status') and hiring_data.get('remote_status'):
                sd['remote_status'] = hiring_data.get('remote_status')
            processed.append(hiring_data)
            
        if intern_fresh_data:
            sd['internships'] = sd.get('internships', []) + intern_fresh_data.get('internships', [])
            sd['fresher_jobs'] = sd.get('fresher_jobs', []) + intern_fresh_data.get('fresher_jobs', [])
            processed.append(intern_fresh_data)

    logger.info(f"Found updates for {len(startups)} startups.")
    
    # Enrichment
    for name, data in startups.items():
        founders_to_enrich = data.get('founders', [])
        if founders_to_enrich:
            data['enriched_founders'] = enrich_founders(name, founders_to_enrich)
            
    # Scoring
    startups = score_startups(startups)
    
    # Report Generation
    if startups:
        html_content = generate_reports(startups)
        
        # Send Email
        send_email(html_content)
        
        # Update History
        update_history(processed)
    else:
        logger.info("No new startup updates found today. Skipping email.")

    logger.info("Run completed successfully.")

if __name__ == "__main__":
    main()
