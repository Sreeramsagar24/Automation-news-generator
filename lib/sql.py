"""
sql.py
Generic MySQL handler with automatic database + table precheck.
"""

from mysql.connector import Error
from datetime import datetime
from .connections import get_mysql_connection
from .utils import open_json


def precheck_database_and_tables(TABLES=None):
    """Ensure the target database and required tables exist."""
    try:
        mysql_cfg = open_json("mysql")
        db_name = mysql_cfg.get("database")

        if not db_name:
            raise ValueError("[ERROR] Database name missing in config.json")

        conn = get_mysql_connection(database=False)
        cur = conn.cursor()

        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;")
        print(f"[INFO] Database check complete or created: {db_name}")
        cur.execute(f"USE `{db_name}`;")

        # Default table schemas (if not passed)
        if TABLES is None:
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

        # Create each table if missing
        for table_name, columns in TABLES.items():
            columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            cur.execute(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({columns_sql});")
            print(f"[INFO] Table '{table_name}' ready.")

        conn.commit()
        cur.close()
        conn.close()
        print("[INFO] Database and all required tables are ready.\n")

    except Exception as e:
        print(f"[ERROR] Database precheck failed: {e}")


def insert_one(table: str, record: dict):
    """Insert a single record into the specified table."""
    if not record:
        print("Skipping empty record.")
        return

    conn = get_mysql_connection(database=True)
    if conn is None:
        print("[ERROR] MySQL connection failed. Skipping insert.")
        return

    cur = conn.cursor()
    try:
        cols = ", ".join(record.keys())
        placeholders = ", ".join(["%s"] * len(record))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        cur.execute(sql, tuple(record.values()))
        conn.commit()
        print(f"[INFO] 1.record inserted into '{table}'.")
    except Error as e:
        print(f"[ERROR] Insert failed: {e}")
    finally:
        cur.close()
        conn.close()


def insert_many(table: str, records: list[dict]):
    """Insert multiple records (list of dicts) into a table."""
    if not records:
        print("[WARN] No records to insert.")
        return

    conn = get_mysql_connection(database=True)
    if conn is None:
        print("[ERROR] MySQL connection failed. Skipping bulk insert.")
        return

    cur = conn.cursor()
    try:
        cols = ", ".join(records[0].keys())
        placeholders = ", ".join(["%s"] * len(records[0]))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        values = [tuple(r.values()) for r in records]
        cur.executemany(sql, values)
        conn.commit()
        print(f"[INFO] {len(records)} records inserted into '{table}'.")
    except Error as e:
        print(f"[ERROR] Bulk insert failed: {e}")
    finally:
        cur.close()
        conn.close()


def fetch_all(table: str, columns: list[str] | None = None):
    """Fetch all rows from a table as a list of dicts."""
    conn = get_mysql_connection(database=True)
    if conn is None:
        print("[ERROR] MySQL connection failed. Cannot fetch data.")
        return []

    cur = conn.cursor(dictionary=True)
    try:
        cols = ", ".join(columns) if columns else "*"
        cur.execute(f"SELECT {cols} FROM {table}")
        data = cur.fetchall()
        print(f"[INFO] Fetched {len(data)} rows from '{table}'.")
        return data
    except Error as e:
        print(f"[ERROR] Fetch failed: {e}")
        return []
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("Running SQL module self-test...\n")

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

    precheck_database_and_tables(TABLES)

    insert_one("news", {
        "headline": "Teacher-approved structured schema test",
        "source": "System",
        "url": "https://example.com",
        "published_at": datetime.now().strftime("%Y-%m-%d"),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    print(fetch_all("news"))
