# app/db.py
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables directly
load_dotenv()

logger = logging.getLogger(__name__)

def get_connection():
    """Get PostgreSQL connection (Sync Method)"""
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "post@2025"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            cursor_factory=RealDictCursor
        )
        logger.info(f"✅ Database connected → {os.getenv('DB_NAME')} @ {os.getenv('DB_HOST')}")
        return conn
    except Exception as e:
        logger.error(f"❌ DB connection failed → {e}")
        raise

@contextmanager
def get_db_cursor():
    """
    Context manager for database cursor handling
    Provides automatic connection and transaction management
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
        logger.debug("✅ Database transaction committed")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Database error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()