"""
emailer.py
-----------
This module contains a function `send_email` that sends an email
with a JSON report attached using the centralized SMTP connection.

Uses get_smtp_connection() from connections.py
Loads email config dynamically from utils.py
Sends JSON report as attachment
Has consistent error handling and logs
"""

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import os
from datetime import datetime
from smtplib import SMTPException
from .utils import open_json
from .connections import get_smtp_connection


def send_email(report_file: str):
    """
    Send an email with the given JSON report attached.
    Args:
        report_file (str): Full path of the report JSON file.

    Returns:
        bool: True if email sent successfully, False otherwise.
    """
    try:

        email_cfg = open_json("email")
        if not email_cfg:
            raise KeyError("[ERROR] 'email' section missing in config file.")

        sender = email_cfg["sender_email"]
        recipients = email_cfg["recipients"]
        subject = f"Automated Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        body_text = "Hello,\n\nPlease find the attached automated JSON report.\n\nRegards,\nAutomation System"


        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))


        if not os.path.exists(report_file):
            raise FileNotFoundError(f"[ERROR] Report file not found: {report_file}")

        with open(report_file, "rb") as f:
            attachment = MIMEApplication(f.read(), Name=os.path.basename(report_file))
        attachment["Content-Disposition"] = f'attachment; filename="{os.path.basename(report_file)}"'
        msg.attach(attachment)

        smtp = get_smtp_connection()
        if smtp is None:
            raise ConnectionError("[ERROR] SMTP connection not established.")

        smtp.sendmail(sender, recipients, msg.as_string())
        print(f"[INFO] Email sent successfully to {recipients}")
        return True

    except (SMTPException, ConnectionError, FileNotFoundError, KeyError) as e:
        print(f"[ERROR] Failed to send email: {e}")
        return False

    except Exception as e:
        print(f"[ERROR] Unexpected error in send_email(): {e}")
        return False
