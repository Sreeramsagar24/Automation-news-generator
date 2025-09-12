# sql.py
import mysql.connector
from datetime import datetime
import json
from .rest import fetch_news, fetch_weather, fetch_currency
def open_json():
    with open('C:\\Users\\SRIRAM\\PycharmProjects\\pythondeveloper\\AUTOMATION_PROJECT\\config\\config.json', 'r') as f:
        data=json.load(f)
    return data
def get_connection():
    details = open_json()
    mysql_cfg = details["mysql"]
    return mysql.connector.connect(
        host=mysql_cfg["host"],
        user=mysql_cfg["user"],
        port=mysql_cfg["port"],
        password=mysql_cfg["password"],
        database=mysql_cfg["database"],
        autocommit=True
    )

def create_tables():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        create table if not exists news (id int auto_increment primary key,headline varchar(500),
        source varchar(100),url varchar(500),published_at varchar(50),fetched_at varchar(50)
        )
    """)
    cur.execute("""
        create table if not exists weather (
            id int auto_increment primary key,
            city varchar(100),
            temperature float,
            humidity float,
            timestamp varchar(50))""")
    cur.execute("""
        create table if not exists currency (id int auto_increment primary key,base varchar(10),
            target varchar(10),rate float,timestamp varchar(50))""")
    cur.close()
    conn.close()
def insert_news(articles):
    conn = get_connection()
    cur = conn.cursor()
    query = """insert into news (headline, source, url, published_at, fetched_at) values (%s, %s, %s, %s, %s)"""
    for a in articles:
        cur.execute(query, (
            a.get("title"),
            a.get("source"),
            a.get("url"),
            a.get("publishedAt"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    cur.close()
    conn.close()
def insert_weather(w):
    conn = get_connection()
    cur = conn.cursor()
    query = ("""
        insert into weather (city, temperature, humidity, timestamp) values (%s, %s, %s, %s)""")
    for w in w:
        cur.execute(query, (
            "Hyderabad",
            w.get("temperature"),
            w.get("humidity"),
            w.get("time")
        ))
    cur.close()
    conn.close()

def insert_currency(rates):
    conn = get_connection()
    cur = conn.cursor()
    query = """
        INSERT INTO currency (base, target, rate, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    for r in rates:
        cur.execute(query, (
            r.get("base"),
            r.get("target"),
            r.get("rate"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    cur.close()
    conn.close()

articles=fetch_news()
weather=fetch_weather()
rates=fetch_currency()
if __name__ == "__main__":
    create_tables()
    print("[INFO] Tables created successfully ")
    insert_news(articles)
    insert_weather(weather)
    insert_currency(rates)