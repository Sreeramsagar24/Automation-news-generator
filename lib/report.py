"""
report.py
----------
Generates dynamic JSON reports using reusable SQL methods.
"""

import json
from datetime import datetime
from .sql import fetch_all
from .utils import get_reports_dir


def generate_report(entry_count=None):
    """
    Generates a report combining data from all tables.
    Uses generic SQL methods (no DB logic here).
    """
    try:
        report_data = {
            "news": fetch_all("news", ["headline", "source", "url", "published_at"])[:entry_count],
            "weather": {},
            "currency": []
        }

        weather = fetch_all("weather", ["city", "temperature", "humidity", "timestamp"])
        if weather:
            report_data["weather"] = weather[-1]

        currency = fetch_all("currency", ["base", "target", "rate", "timestamp"])
        if currency:
            report_data["currency"].append(currency[-1])

        reports_dir = get_reports_dir()
        file_path = reports_dir / f"auto_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4)

        print(f"[INFO] Report generated: {file_path}")
        return str(file_path)

    except Exception as e:
        print(f"[ERROR] Report generation failed: {e}")
        return None
