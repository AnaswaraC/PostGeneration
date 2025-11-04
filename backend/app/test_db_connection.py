# app/test_db_connection.py
import sys
import os

# Fix imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from app.db import get_connection

def test():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print("✅ PostgreSQL Connected Successfully")
        print("PostgreSQL Version:", result)
        cursor.close()
        conn.close()
    except Exception as e:
        print("❌ Connection Failed:", e)

if __name__ == "__main__":
    test()