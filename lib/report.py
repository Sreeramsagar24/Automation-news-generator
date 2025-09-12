import json
import os
from datetime import datetime
from .sql import get_connection

def generate_report():
    conn=get_connection()
    cur=conn.cursor(dictionary=True)
    report={"news":[],"weather":[],"currency":[]}
    cur.execute("SELECT headline, source, url, published_at from news ORDER BY id DESC LIMIT 5")
    report["news"] = cur.fetchall()

    cur.execute("SELECT city, temperature, humidity, timestamp from weather ORDER BY id DESC LIMIT 1")
    weather = cur.fetchone()
    if weather:
        report["weather"]=weather

    cur.execute("SELECT base, target, rate, timestamp from currency ORDER BY id DESC LIMIT 1")
    currency = cur.fetchone()
    if currency:
        report["currency"].append(currency)
    cur.close()
    conn.close()

    output_file="reports"
    if not os.path.exists(output_file):
        os.makedirs(output_file,exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    json_file = f"{output_file}/auto_report_{now}.json"

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    return json_file

if __name__ == "__main__":
    generate_report()

