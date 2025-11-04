# app/auth/signup.py
import logging
from typing import Dict, Any, Optional
from app.repositories.user_repo import UserRepository
from app.models.user import UserCreate, UserResponse

logger = logging.getLogger(__name__)

class SignupService:
    """Service layer for user registration business logic"""
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        # Add more validation as needed
        return True, ""
    
    @staticmethod
    def create_user(user_data: UserCreate, cursor) -> UserResponse:
        """Create new user - pure business logic"""
        user_repo = UserRepository(cursor)
        
        # Check if user exists by email
        if user_repo.get_user_by_email(user_data.email):
            raise ValueError("Email already registered")
        
        # Check if username exists
        if user_repo.get_user_by_username(user_data.username):
            raise ValueError("Username already taken")
        
        # Validate password
        is_valid, error_msg = SignupService.validate_password(user_data.password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Create user (hash_password is called internally in user_repo.create_user)
        user = user_repo.create_user(
            email=user_data.email,
            password=user_data.password,
            username=user_data.username
        )
        
        if not user:
            raise ValueError("Failed to create user account")
        
        return UserResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            created_at=user['created_at'],
            last_login=user['last_login'],
            is_active=user['is_active']
        )

def handle_signup(user_data: UserCreate, db_cursor) -> Dict[str, Any]:
    """
    High-level signup handler function
    """
    user_repo = UserRepository(db_cursor)
    
    # Check if user exists by email
    if user_repo.get_user_by_email(user_data.email):
        return {
            'success': False,
            'message': 'User with this email already exists',
            'status_code': 400
        }
    
    # Check if username exists
    if user_repo.get_user_by_username(user_data.username):
        return {
            'success': False,
            'message': 'Username already taken',
            'status_code': 400
        }
    
    # Create user
    user = user_repo.create_user(
        email=user_data.email,
        password=user_data.password,
        username=user_data.username
    )
    
    if user:
        user_response = UserResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            created_at=user['created_at'],
            last_login=user['last_login'],
            is_active=user['is_active']
        )
        
        return {
            'success': True,
            'message': 'User created successfully',
            'user': user_response,
            'status_code': 201
        }
    else:
        return {
            'success': False,
            'message': 'Failed to create user account',
            'user': None,
            'status_code': 400
        }

# Alternative simplified version for direct use
def create_new_user(user_data: UserCreate, db_cursor) -> UserResponse:
    """
    Simplified signup function for direct use in routes
    """
    user_repo = UserRepository(db_cursor)
    
    # Check if user exists by email
    if user_repo.get_user_by_email(user_data.email):
        raise ValueError("User with this email already exists")
    
    # Check if username exists
    if user_repo.get_user_by_username(user_data.username):
        raise ValueError("Username already taken")
    
    # Create user
    user = user_repo.create_user(
        email=user_data.email,
        password=user_data.password,
        username=user_data.username
    )
    
    if not user:
        raise ValueError("Failed to create user account")
    
    return UserResponse(
        id=user['id'],
        email=user['email'],
        username=user['username'],
        created_at=user['created_at'],
        last_login=user['last_login'],
        is_active=user['is_active']
    )