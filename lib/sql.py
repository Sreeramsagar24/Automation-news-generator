# sql.
"""
sql.py
This module contains functions to create MySQL tables and insert news, weather,
and currency data fetched from APIs.
"""
from datetime import datetime
import json
import os
import mysql.connector
from .rest import fetch_news, fetch_weather, fetch_currency


def open_json():
    """
    Opens and loads the JSON configuration file
    :return: Configuration details from config.json
    """
    # Get base directory of project
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, 'config', 'config.json')

    with open(config_path, 'r', encoding="utf-8") as f:
        data = json.load(f)
    return data
def get_connection():
    """
    Creates a MySQL connection using config details
    :return:mysql.connector.connection.MySQLConnection: Database connection object
    """
    details = open_json()
    mysql_cfg = details["mysql"]
    print("[DEBUG] Connecting to MySQL with:", mysql_cfg)
    return mysql.connector.connect(
        host=mysql_cfg["host"],
        user=mysql_cfg["user"],
        port=mysql_cfg["port"],
        password=mysql_cfg["password"],
        database=mysql_cfg["database"],
        autocommit=True
    )

def create_tables():
    """
    Creates tables for news, weather, and currency if they do not exist
    """
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
    """
    :param articles: Inserts news articles into the news table
    """
    conn = get_connection()
    cur = conn.cursor()
    query = """insert into news (headline, source, url, published_at, fetched_at)
                values (%s, %s, %s, %s, %s)"""
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
    """
    :param w: Inserts weather data into the weather table
    """
    conn = get_connection()
    cur = conn.cursor()
    query = """
        insert into weather (city, temperature, humidity, timestamp) values (%s, %s, %s, %s)"""
    for i in w:
        cur.execute(query, (
            "Hyderabad",
            i.get("temperature"),
            i.get("humidity"),
            i.get("time")
        ))
    cur.close()
    conn.close()

def insert_currency(rates):
    """
    :param rates: Inserts currency rates into the currency table
    """
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



def main():
    """
    :return:
    """
    create_tables()
    print("[INFO] Tables created successfully")

    articles_data = fetch_news()
    weather_data = fetch_weather()
    rates_data = fetch_currency()

    insert_news(articles_data)
    insert_weather(weather_data)
    insert_currency(rates_data)
    print("[INFO] Data inserted successfully")


if __name__ == "__main__":
    main()
