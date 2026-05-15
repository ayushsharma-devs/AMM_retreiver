import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "audit.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            user_agent TEXT NOT NULL,
            action TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_acceptance(ip_address: str, user_agent: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    cursor.execute('''
        INSERT INTO audit_logs (timestamp, ip_address, user_agent, action)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, ip_address, user_agent, "Accepted Disclaimer"))
    conn.commit()
    conn.close()
