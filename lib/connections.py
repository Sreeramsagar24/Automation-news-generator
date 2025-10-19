"""
connections.py
Centralized connection manager for MySQL, SMTP, and SSH.
Handles lazy initialization, reconnects, and auto database selection.
"""

import mysql.connector
from mysql.connector import MySQLConnection, Error
import smtplib
from smtplib import SMTP
import paramiko
from paramiko import SSHClient
from .utils import open_json

# Global singletons
_mysql_conn: MySQLConnection | None = None
_smtp_conn: SMTP | None = None
_ssh_conn: SSHClient | None = None


def get_mysql_connection(database=True) -> MySQLConnection | None:
    """
    Lazily create and return a reusable MySQL connection.
    Automatically selects the database (if database=True).
    """
    global _mysql_conn

    mysql_cfg = open_json("mysql")
    if not mysql_cfg:
        print("[ERROR] 'mysql' section not found in config file.")
        return None

    # Reuse existing connection if alive — but check if DB is selected
    if _mysql_conn is not None:
        try:
            _mysql_conn.ping(reconnect=True, attempts=1, delay=0)
            if database and not _mysql_conn.database:
                _mysql_conn.database = mysql_cfg.get("database")
            return _mysql_conn
        except Error:
            print("[WARN]  Existing MySQL connection lost. Reconnecting...")
            _mysql_conn = None

    conn_args = {
        "host": mysql_cfg["host"],
        "user": mysql_cfg["user"],
        "password": mysql_cfg["password"],
        "port": mysql_cfg.get("port", 3306),
        "autocommit": True
    }

    if database:
        conn_args["database"] = mysql_cfg.get("database")

    try:
        _mysql_conn = mysql.connector.connect(**conn_args)
        print(f"[INFO]  MySQL connected successfully (DB: {mysql_cfg.get('database')}).")
        return _mysql_conn
    except Error as e:
        print(f"[ERROR]  MySQL connection failed → host={mysql_cfg['host']}:{mysql_cfg['port']}, user={mysql_cfg['user']}")
        print(f"       Details: {e}")
        _mysql_conn = None
        return None



def get_smtp_connection() -> SMTP | None:
    """
    Lazily create and return a reusable SMTP (email) connection.
    """
    global _smtp_conn

    email_cfg = open_json("email")
    if not email_cfg:
        print("[ERROR] 'email' section missing in config file.")
        return None

    # Check if already connected
    if _smtp_conn is not None:
        try:
            status = _smtp_conn.noop()[0]
            if status == 250:
                return _smtp_conn
        except Exception:
            _smtp_conn = None  # Reconnect below

    try:
        _smtp_conn = smtplib.SMTP(email_cfg["smtp_server"], email_cfg["smtp_port"])
        _smtp_conn.starttls()
        _smtp_conn.login(email_cfg["sender_email"], email_cfg["password"])
        print(f"[INFO] SMTP connected successfully ({email_cfg['sender_email']}).")
        return _smtp_conn
    except Exception as e:
        print(f"[ERROR] SMTP connection failed: {e}")
        _smtp_conn = None
        return None



def get_ssh_connection() -> SSHClient | None:
    """
    Lazily create and return a reusable SSH connection.
    """
    global _ssh_conn

    ssh_cfg = open_json("ssh")
    if not ssh_cfg:
        print("[ERROR] 'ssh' section not found in config file.")
        return None

    # If already active
    if _ssh_conn is not None:
        try:
            transport = _ssh_conn.get_transport()
            if transport and transport.is_active():
                return _ssh_conn
        except Exception:
            _ssh_conn = None

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=ssh_cfg["host"],
            port=ssh_cfg["port"],
            username=ssh_cfg["username"],
            password=ssh_cfg["password"],
            timeout=10
        )
        _ssh_conn = ssh
        print(f"[INFO] SSH connected successfully ({ssh_cfg['host']}:{ssh_cfg['port']}).")
        return _ssh_conn
    except Exception as e:
        print(f"[ERROR] SSH connection failed: {e}")
        _ssh_conn = None
        return None


def close_all_connections():
    """Safely close all open connections."""
    global _mysql_conn, _smtp_conn, _ssh_conn
    if _mysql_conn:
        try:
            _mysql_conn.close()
            print("[INFO] MySQL connection closed.")
        except Exception:
            pass
        _mysql_conn = None

    if _smtp_conn:
        try:
            _smtp_conn.quit()
            print("[INFO] SMTP connection closed.")
        except Exception:
            pass
        _smtp_conn = None
    if _ssh_conn:
        try:
            _ssh_conn.close()
            print("[INFO] SSH connection closed.")
        except Exception:
            pass
        _ssh_conn = None

def close_mysql_connection():
    """Safely close only the MySQL connection."""
    global _mysql_conn
    if _mysql_conn:
        try:
            _mysql_conn.close()
            print("[INFO] MySQL connection closed.")
        except Exception as e:
            print(f"[WARN] Error closing MySQL connection: {e}")
        _mysql_conn = None


def close_smtp_connection():
    """Safely close only the SMTP (email) connection."""
    global _smtp_conn
    if _smtp_conn:
        try:
            _smtp_conn.quit()
            print("[INFO] SMTP connection closed.")
        except Exception as e:
            print(f"[WARN] Error closing SMTP connection: {e}")
        _smtp_conn = None


def close_ssh_connection():
    """Safely close only the SSH connection."""
    global _ssh_conn
    if _ssh_conn:
        try:
            _ssh_conn.close()
            print("[INFO] SSH connection closed.")
        except Exception as e:
            print(f"[WARN] Error closing SSH connection: {e}")
        _ssh_conn = None
