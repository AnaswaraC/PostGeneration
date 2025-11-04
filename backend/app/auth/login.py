# app/auth/login.py
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.repositories.user_repo import UserRepository
from app.models.user import UserLogin, UserResponse
from app.auth.jwt_handler import create_access_token

logger = logging.getLogger(__name__)

class LoginService:
    """Service layer for user authentication business logic"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def validate_login_data(self, login_data: UserLogin) -> Dict[str, Any]:
        """
        Validate login input data
        """
        errors = {}
        
        # Email validation
        if not login_data.email or '@' not in login_data.email:
            errors['email'] = 'Valid email is required'
        
        # Password validation
        if not login_data.password or len(login_data.password) < 1:
            errors['password'] = 'Password is required'
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[Dict[str, Any]]:
        """
        Authenticate user credentials and return user data if valid
        """
        try:
            # Validate input data
            validation_result = self.validate_login_data(login_data)
            if not validation_result['is_valid']:
                logger.warning(f"Login validation failed for {login_data.email}: {validation_result['errors']}")
                return None
            
            # Attempt authentication
            user = self.user_repo.authenticate_user(login_data.email, login_data.password)
            
            if not user:
                logger.warning(f"Failed authentication attempt for: {login_data.email}")
                return None
            
            if not user['is_active']:
                logger.warning(f"Login attempt for inactive account: {login_data.email}")
                return {'user': user, 'error': 'Account is deactivated'}
            
            # Update last login timestamp
            self.user_repo.update_last_login(user['id'])
            
            logger.info(f"Successful login for: {login_data.email}")
            return {'user': user, 'error': None}
            
        except Exception as e:
            logger.error(f"Authentication error for {login_data.email}: {str(e)}")
            return None
    
    def create_login_response(self, user_data: dict) -> Dict[str, Any]:
        """
        Create login response with JWT token
        """
        try:
            # Create access token
            access_token = create_access_token(
                data={"sub": user_data['email'], "user_id": user_data['id']}
            )
            
            # Prepare user response
            user_response = UserResponse(
                id=user_data['id'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                created_at=user_data['created_at'],
                last_login=user_data['last_login'],
                is_active=user_data['is_active']
            )
            
            return {
                'access_token': access_token,
                'token_type': 'bearer',
                'user': user_response
            }
            
        except Exception as e:
            logger.error(f"Error creating login response for {user_data['email']}: {str(e)}")
            return None
    
    def handle_failed_login(self, email: str, failure_reason: str) -> Dict[str, Any]:
        """
        Handle failed login attempts (could be extended for rate limiting)
        """
        logger.warning(f"Login failed for {email}: {failure_reason}")
        
        # Here you could implement:
        # - Rate limiting
        # - Failed attempt tracking
        # - Account lockout after multiple failures
        
        return {
            'success': False,
            'error': failure_reason,
            'can_retry': True
        }

def handle_login(login_data: UserLogin, db_cursor) -> Dict[str, Any]:
    """
    High-level login handler function
    """
    user_repo = UserRepository(db_cursor)
    login_service = LoginService(user_repo)
    
    # Attempt authentication
    auth_result = login_service.authenticate_user(login_data)
    
    if not auth_result:
        return {
            'success': False,
            'message': 'Authentication failed',
            'status_code': 401
        }
    
    if auth_result['error']:
        return {
            'success': False,
            'message': auth_result['error'],
            'status_code': 403 if auth_result['error'] == 'Account is deactivated' else 401
        }
    
    # Create login response with token
    login_response = login_service.create_login_response(auth_result['user'])
    
    if not login_response:
        return {
            'success': False,
            'message': 'Failed to create login session',
            'status_code': 500
        }
    
    return {
        'success': True,
        'message': 'Login successful',
        'data': login_response,
        'status_code': 200
    }

# Alternative simplified version for direct use
def authenticate_and_create_token(login_data: UserLogin, db_cursor) -> Dict[str, Any]:
    """
    Simplified login function for direct use in routes
    """
    user_repo = UserRepository(db_cursor)
    
    # Authenticate user
    user = user_repo.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise ValueError("Invalid email or password")
    
    if not user['is_active']:
        raise ValueError("Account is deactivated")
    
    # Update last login
    user_repo.update_last_login(user['id'])
    
    # Create token
    access_token = create_access_token(
        data={"sub": user['email'], "user_id": user['id']}
    )
    
    # Prepare response
    user_response = UserResponse(
        id=user['id'],
        email=user['email'],
        full_name=user['full_name'],
        created_at=user['created_at'],
        last_login=user['last_login'],
        is_active=user['is_active']
    )
    
    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'user': user_response
    }

class LoginAttemptTracker:
    """
    Optional class for tracking login attempts and implementing rate limiting
    """
    
    def __init__(self):
        self.failed_attempts = {}
    
    def record_failed_attempt(self, email: str):
        """Record a failed login attempt"""
        if email not in self.failed_attempts:
            self.failed_attempts[email] = {
                'count': 0,
                'first_attempt': datetime.utcnow()
            }
        
        self.failed_attempts[email]['count'] += 1
        self.failed_attempts[email]['last_attempt'] = datetime.utcnow()
    
    def should_block_login(self, email: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Check if login should be blocked due to too many failed attempts"""
        if email not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[email]
        time_since_first = datetime.utcnow() - attempts['first_attempt']
        
        # Reset if outside time window
        if time_since_first.total_seconds() > window_minutes * 60:
            del self.failed_attempts[email]
            return False
        
        return attempts['count'] >= max_attempts
    
    def reset_attempts(self, email: str):
        """Reset failed attempts for an email (on successful login)"""
        if email in self.failed_attempts:
            del self.failed_attempts[email]

# Global instance for login attempt tracking
login_tracker = LoginAttemptTracker()