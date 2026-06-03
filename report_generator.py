import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template
from config import HTML_REPORT_FILE, CSV_REPORT_FILE, XLSX_REPORT_FILE, HOT_STARTUPS_FILE, logger
from datetime import datetime

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #2C3E50; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #F2F2F2; font-weight: bold; }
        .stats { background: #E8F8F5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .cold-email { background: #FEF9E7; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>Indian Startup Funding & Hiring Report - {{ date }}</h1>
    
    <div class="stats">
        <h2>SECTION 6: Summary Statistics</h2>
        <ul>
            <li>Number of funding announcements: {{ stats.funding_count }}</li>
            <li>Number of startups hiring: {{ stats.hiring_count }}</li>
            <li>Number of internship opportunities: {{ stats.internship_count }}</li>
            <li>Number of fresher opportunities: {{ stats.fresher_count }}</li>
        </ul>
    </div>

    <div class="cold-email">
        <h2>SECTION 7: Top Startups to Cold Email Today</h2>
        <table>
            <tr><th>Startup</th><th>Reason</th><th>Placement Score</th></tr>
            {% for s in cold_email_targets %}
            <tr>
                <td>{{ s.name }}</td>
                <td>{{ s.reason }}</td>
                <td>{{ s.placement_score }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <h2>SECTION 1: Funding Announcements</h2>
    <table>
        <tr><th>Startup</th><th>Funding</th><th>Stage</th><th>Investors</th><th>Founders</th><th>Hiring Soon?</th></tr>
        {% for f in funding %}
        <tr>
            <td>{{ f.startup_name }}</td>
            <td>{{ f.funding_amount }} {{ f.currency }}</td>
            <td>{{ f.funding_stage }}</td>
            <td>{{ f.all_investors | join(', ') }}</td>
            <td>{{ f.founders | join(', ') }}</td>
            <td>{{ f.likely_hiring_soon }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>SECTION 2: Top Startups Likely Hiring</h2>
    <table>
        <tr><th>Startup</th><th>Placement Score</th><th>Open Roles</th><th>Career Page</th></tr>
        {% for h in hiring %}
        <tr>
            <td>{{ h.startup_name }}</td>
            <td>{{ h.placement_score }}</td>
            <td>{{ h.open_roles | join(', ') }}</td>
            <td>{{ h.careers_page }}</td>
        </tr>
        {% endfor %}
    </table>

    <h2>SECTION 3: Internship Opportunities</h2>
    <table>
        <tr><th>Company</th><th>Role</th><th>Location</th><th>Remote</th><th>Apply</th></tr>
        {% for i in internships %}
        <tr>
            <td>{{ i.startup_name }}</td>
            <td>{{ i.role }}</td>
            <td>{{ i.location }}</td>
            <td>{{ i.remote_status }}</td>
            <td><a href="{{ i.apply_link }}">Apply</a></td>
        </tr>
        {% endfor %}
    </table>

    <h2>SECTION 4: Fresher Opportunities</h2>
    <table>
        <tr><th>Company</th><th>Role</th><th>Experience</th><th>Location</th><th>Apply</th></tr>
        {% for f in freshers %}
        <tr>
            <td>{{ f.startup_name }}</td>
            <td>{{ f.role }}</td>
            <td>{{ f.experience_required }}</td>
            <td>{{ f.location }}</td>
            <td><a href="{{ f.apply_link }}">Apply</a></td>
        </tr>
        {% endfor %}
    </table>

    <h2>SECTION 5: Founder Directory</h2>
    <table>
        <tr><th>Startup</th><th>Founder</th><th>LinkedIn</th></tr>
        {% for f in founders %}
        <tr>
            <td>{{ f.startup_name }}</td>
            <td>{{ f.name }} <br><small>{{ f.title }}</small></td>
            <td><a href="{{ f.linkedin_url }}">LinkedIn</a></td>
        </tr>
        {% endfor %}
    </table>

</body>
</html>
"""

def generate_reports(startups_dict):
    """
    Generates HTML, CSV, and XLSX reports based on processed startup data.
    """
    date_str = datetime.now().strftime("%B %d, %Y")
    
    funding_list = []
    hiring_list = []
    internships_list = []
    freshers_list = []
    founders_list = []
    cold_email_targets = []
    
    flat_data = []
    
    for name, data in startups_dict.items():
        if data.get('recent_funding'):
            funding_list.append(data)
            
        if data.get('open_roles') or data.get('hiring_score', 0) > 0:
            hiring_list.append(data)
            
        for intern in data.get('internships', []):
            intern['startup_name'] = name
            internships_list.append(intern)
            
        for fresh in data.get('fresher_jobs', []):
            fresh['startup_name'] = name
            freshers_list.append(fresh)
            
        for founder in data.get('enriched_founders', []):
            founder['startup_name'] = name
            founders_list.append(founder)
            
        # Determine cold email targets (high placement score)
        if data.get('placement_score', 0) >= 40:
            reason = []
            if data.get('recent_funding'):
                reason.append(f"Raised {data.get('funding_amount', '')}")
            if data.get('open_roles'):
                reason.append("Hiring engineers")
            if data.get('internships'):
                reason.append("Opened internship program")
            
            cold_email_targets.append({
                "name": name,
                "reason": " and ".join(reason) if reason else "High placement score",
                "placement_score": data.get('placement_score', 0)
            })
            
        # Flat data for CSV/XLSX
        flat_data.append({
            "Startup": name,
            "Funding Amount": data.get('funding_amount', ''),
            "Hiring Score": data.get('hiring_score', 0),
            "Placement Score": data.get('placement_score', 0),
            "Careers Page": data.get('careers_page', ''),
            "Open Roles": ", ".join(data.get('open_roles', [])),
            "Founder": ", ".join([f['name'] for f in data.get('enriched_founders', [])]),
            "Website": data.get('company_website', '')
        })

    # Sort lists
    hiring_list.sort(key=lambda x: x.get('placement_score', 0), reverse=True)
    cold_email_targets.sort(key=lambda x: x.get('placement_score', 0), reverse=True)
    
    stats = {
        "funding_count": len(funding_list),
        "hiring_count": len(hiring_list),
        "internship_count": len(internships_list),
        "fresher_count": len(freshers_list)
    }
    
    # 1. HTML Report
    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        date=date_str,
        stats=stats,
        funding=funding_list,
        hiring=hiring_list,
        internships=internships_list,
        freshers=freshers_list,
        founders=founders_list,
        cold_email_targets=cold_email_targets[:10] # Top 10
    )
    with open(HTML_REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # 2. CSV / XLSX Exports
    df = pd.DataFrame(flat_data)
    df = df.sort_values(by="Placement Score", ascending=False)
    
    df.to_csv(CSV_REPORT_FILE, index=False)
    df.to_csv(HOT_STARTUPS_FILE, index=False)
    df.to_excel(XLSX_REPORT_FILE, index=False)
    
    logger.info(f"Generated HTML, CSV, and XLSX reports in reports directory.")
    return html_content
