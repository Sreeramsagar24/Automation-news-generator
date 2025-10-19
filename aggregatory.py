"""
aggregator.py
Main orchestrator:
Fetches data from APIs, inserts into DB,
generates JSON reports, sends emails, and cleans old reports.

Uses dictionary-based schema (no SQL strings)
Fully modular and dynamic
Error handled and production ready
"""
import argparse
import os
import sys
from datetime import datetime, timedelta
from lib.sql import precheck_database_and_tables, insert_many
from lib.rest import fetch_news, fetch_weather, fetch_currency
from lib.report import generate_report
from lib.emailer import send_email
from lib.utils import get_reports_dir


entry_count=5
services=["news","weather","currency"]
TABLES = {
    "news": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "headline": "VARCHAR(500)",
        "source": "VARCHAR(100)",
        "url": "VARCHAR(500)",
        "published_at": "VARCHAR(50)",
        "fetched_at": "VARCHAR(50)"
    },
    "weather": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "city": "VARCHAR(100)",
        "temperature": "FLOAT",
        "humidity": "FLOAT",
        "timestamp": "VARCHAR(50)"
    },
    "currency": {
        "id": "INT AUTO_INCREMENT PRIMARY KEY",
        "base": "VARCHAR(10)",
        "target": "VARCHAR(10)",
        "rate": "FLOAT",
        "timestamp": "VARCHAR(50)"
    }
}


def fetch_and_report():
    """Fetch data, insert into DB, generate JSON report, and send email."""
    try:
        print("\n[INFO] Starting data fetch...")




        if "news" in services:
            news_data = fetch_news()
            if news_data:
                insert_many("news", [
                    {
                        "headline": n.get("title"),
                        "source": n.get("source"),
                        "url": n.get("url"),
                        "published_at": n.get("publishedAt"),
                        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    } for n in news_data
                ])
            else:
                print("[WARN] No news data fetched.")

        if "weather" in services:
            weather_data=fetch_weather()
            if weather_data:
                insert_many("weather", [
                    {
                        "city": "Auto-Detected",
                        "temperature": w.get("temperature"),
                        "humidity": w.get("humidity"),
                        "timestamp": w.get("time")
                    } for w in weather_data
                ])
            else:
                print("[WARN] No weather data fetched.")

        if "currency" in services:
            currency_data = fetch_currency()
            if currency_data:
                insert_many("currency", [
                    {
                        "base": c.get("base"),
                        "target": c.get("target"),
                        "rate": c.get("rate"),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    } for c in currency_data
                ])
            else:
                print("[WARN] No currency data fetched.")

        # Generate report and send email
        print("[INFO] Generating report and sending email...")
        report_file = generate_report()
        if report_file:
            send_email(report_file)
            print(f"[INFO] Report generated and emailed successfully: {report_file}")
        else:
            print("[WARN] Report generation failed. Email not sent.")

    except Exception as e:
        print(f"[ERROR] Error in fetch_and_report: {e}")


def clean_reports(days=30):
    """
    Delete reports older than `days` days from the /reports directory.
    """
    reports_dir = get_reports_dir()
    cutoff_time = datetime.now() - timedelta(days=days)
    deleted_files = 0

    for file_name in os.listdir(reports_dir):
        if file_name.endswith(".json"):
            file_path = os.path.join(reports_dir, file_name)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_time:
                os.remove(file_path)
                deleted_files += 1

    print(f"[INFO] Old reports deleted: {deleted_files}")

if __name__ == "__main__":
    try:
        print("\n Starting Automated Data Aggregator...\n")
        parser=argparse.ArgumentParser(description="aggregator CLI tool")
        parser.add_argument("-c","--count",type=int,help="no of entries to be returned by the tool (default=5).Max is 10")
        parser.add_argument("-s", "--service",type=str,help="services to return (comma seperated) supported values are:news,weather,currency")
        args=parser.parse_args()
        if args.count:
            if args.count>10:
                raise Exception("max count supported is 10,please select count value less than 10")
            entry_count=args.count

        if args.service:
            input_svc=args.service.split(",")
            for svc in input_svc:
                if svc not in services:
                    raise Exception(f"input service {svc} is invalid, valid services are {services}")
            services=input_svc
        print(f"entry count {entry_count}")
        print(f"services {services}")
        # Step 1: Ensure database and tables exist
        precheck_database_and_tables(TABLES)

        # Step 2: Fetch data → Insert into DB → Generate Report → Send Email
        fetch_and_report()
        # Step 3: Clean up old reports
        clean_reports(days=30)

        print("\n Automation completed successfully.\n")
    except Exception as err:
        print(f"[ERROR]: {err}")
        sys.exit(1)