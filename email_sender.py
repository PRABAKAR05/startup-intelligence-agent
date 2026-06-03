import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENT_EMAIL, logger
from datetime import datetime

def send_email(html_content):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD or not RECIPIENT_EMAIL:
        logger.error("Email credentials not configured properly.")
        return

    date_str = datetime.now().strftime("%B %d, %Y")
    subject = f"Indian Startup Funding & Hiring Report - {date_str}"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL

    part = MIMEText(html_content, 'html')
    msg.attach(part)

    try:
        # Standard Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        logger.info(f"Successfully sent daily report email to {RECIPIENT_EMAIL}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Test sending email
    send_email("<h1>Test Email</h1><p>This is a test.</p>")
