 # lib/emailer.py
"""
emailer.py
This module contains a function `send_email` that sends an email with a JSON report attached.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import json
from datetime import datetime
from smtplib import SMTPException

def send_email(report_file):
    """
    Sends an email with the given report file attached.
    Parameters:
        report_file: The path to the report file to attach.
    Returns:
        None
    """
    with open("C:\\Users\\SRIRAM\\PycharmProjects\\pythondeveloper\\"
              "AUTOMATION_PROJECT\\config\\config.json",encoding="utf-8") as f:
        cfg = json.load(f)
    email_cfg = cfg["email"]
    msg = MIMEMultipart()
    msg["From"] = email_cfg["sender_email"]
    msg["To"] = ", ".join(email_cfg["recipients"])
    msg["Subject"] = f"Automated Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    msg.attach(MIMEText("Please find the attached JSON report.", "plain"))

    with open(report_file, "rb") as f:
        attachment = MIMEApplication(f.read(), Name=report_file.split("/")[-1])
    attachment['Content-Disposition'] = f'attachment; filename="{report_file.split("/")[-1]}"'
    msg.attach(attachment)

    try:
        server = smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"])
        server.starttls()
        server.login(email_cfg["sender_email"], email_cfg["password"])
        server.sendmail(email_cfg["sender_email"], email_cfg["recipients"], msg.as_string())
        server.quit()
        print(f" Email sent successfully to {email_cfg['recipients']}")
    except SMTPException as e:
        print(f" Failed to send email: {e}")
