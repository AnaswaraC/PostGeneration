# app/repositories/user_repo.py
import logging
import uuid
from datetime import datetime
from app.auth.hash_utils import hash_password, verify_password

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_user_by_email(self, email: str):
        self.cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return self.cursor.fetchone()

    def get_user_by_username(self, username: str):
        self.cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return self.cursor.fetchone()

    def get_user_by_id(self, user_id: str):
        self.cursor.execute(
            "SELECT id, email, username, created_at, last_login, is_active FROM users WHERE id = %s", 
            (user_id,)
        )
        return self.cursor.fetchone()

    def create_user(self, email: str, password: str, username: str = None):
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        created_at = datetime.utcnow()
        
        self.cursor.execute(
            """
            INSERT INTO users (id, email, hashed_password, username, created_at) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING id, email, username, created_at, last_login, is_active
            """,
            (user_id, email, hashed_password, username, created_at)
        )
        
        result = self.cursor.fetchone()
        logger.info(f"✅ User created: {email} with username: {username}")
        return result

    def authenticate_user(self, email: str, password: str):
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user['hashed_password']):
            return None
            
        # Update last login timestamp
        self.update_last_login(user['id'])
        return user

    def update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        self.cursor.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), user_id)
        )

    def update_user(self, user_id: str, **kwargs):
        """Update user fields dynamically"""
        if not kwargs:
            return None
            
        set_clause = ", ".join([f"{key} = %s" for key in kwargs.keys()])
        values = list(kwargs.values())
        values.append(user_id)
        
        self.cursor.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s RETURNING id, email, username, created_at, last_login, is_active",
            values
        )
        return self.cursor.fetchone()

    def deactivate_user(self, user_id: str):
        """Deactivate user account"""
        self.cursor.execute(
            "UPDATE users SET is_active = false WHERE id = %s RETURNING id, email, is_active",
            (user_id,)
        )
        return self.cursor.fetchone()

    def get_all_active_users(self):
        """Get all active users (for admin purposes)"""
        self.cursor.execute(
            "SELECT id, email, username, created_at, last_login, is_active FROM users WHERE is_active = true ORDER BY created_at DESC"
        )
        return self.cursor.fetchall()