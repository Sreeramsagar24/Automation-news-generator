# lib/emailer.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import json
from datetime import datetime
def send_email(report_file):
    with open("C:\\Users\\SRIRAM\\PycharmProjects\\pythondeveloper\\AUTOMATION_PROJECT\\config\\config.json") as f:
        cfg = json.load(f)
    EMAIL_CFG = cfg["email"]
    msg = MIMEMultipart()
    msg["From"] = EMAIL_CFG["sender_email"]
    msg["To"] = ", ".join(EMAIL_CFG["recipients"])
    msg["Subject"] = f"Automated Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    msg.attach(MIMEText("Please find the attached JSON report.", "plain"))

    with open(report_file, "rb") as f:
        attachment = MIMEApplication(f.read(), Name=report_file.split("/")[-1])
    attachment['Content-Disposition'] = f'attachment; filename="{report_file.split("/")[-1]}"'
    msg.attach(attachment)

    try:
        server = smtplib.SMTP(EMAIL_CFG["smtp_server"], EMAIL_CFG["smtp_port"])
        server.starttls()
        server.login(EMAIL_CFG["sender_email"], EMAIL_CFG["password"])
        server.sendmail(EMAIL_CFG["sender_email"], EMAIL_CFG["recipients"], msg.as_string())
        server.quit()
        print(f" Email sent successfully to {EMAIL_CFG['recipients']}")
    except Exception as e:
        print(f" Failed to send email: {e}")
