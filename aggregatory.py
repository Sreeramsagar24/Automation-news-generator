import os
import time
from datetime import datetime, timedelta
from lib.sql import create_tables, insert_news, insert_weather, insert_currency
from lib.rest import fetch_news, fetch_weather, fetch_currency
from lib.report import generate_report
from lib.emailer import send_email


def fetch_and_report():
    print("[INFO] Fetching data and generating report...")
    create_tables()
    news_data = fetch_news()
    weather_data = fetch_weather()
    currency_data = fetch_currency()
    if news_data:
        insert_news(news_data)
    if weather_data:
        insert_weather(weather_data)
    if currency_data:
        insert_currency(currency_data)

    report_file = generate_report()
    send_email(report_file)
    print(f" Report generated and sent: {report_file}")
    

def clean_reports():
    reports_dir = "/home/ubuntu/AUTOMATION_PROJECT/reports"
    if not os.path.exists(reports_dir):
        print("Error: Reports directory does not exist.")
        return

    cutoff_time = datetime.now() - timedelta(days=30)
    deleted_files = 0

    for file_name in os.listdir(reports_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(reports_dir, file_name)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_time:
                os.remove(file_path)
                deleted_files += 1

    print(f"Old reports deleted: {deleted_files}")


if __name__ == "__main__":
    # Option 1: Always fetch and send
    fetch_and_report()

    # Option 2: Also clean old reports after fetching
    clean_reports()

    # If you want them to run at different times,
    # you can separate into two scripts: one for fetch, one for clean.
