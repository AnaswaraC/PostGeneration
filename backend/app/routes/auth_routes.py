# app/routes/auth_routes.py
import logging
from fastapi import APIRouter, HTTPException, status, Header, Depends
from app.db import get_db_cursor
from app.models.user import UserCreate, UserResponse, UserLogin, Token
from app.auth.signup import SignupService
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from app.repositories.user_repo import UserRepository
from app.auth.auth_dependency import get_current_user
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate):
    """
    Register new user account
    """
    with get_db_cursor() as cursor:
        try:
            user = SignupService.create_user(user_data, cursor)
            logger.info(f"New user registered: {user_data.email}")
            return user
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Signup error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/login", response_model=Token)
def login(login_data: UserLogin):
    """
    User login - returns access token
    """
    with get_db_cursor() as cursor:
        user_repo = UserRepository(cursor)
        user = user_repo.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            logger.warning(f"Failed login attempt: {login_data.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.get('is_active', True):
            raise HTTPException(status_code=403, detail="Account deactivated")
        
        # Create tokens
        token_data = {
            "sub": user['email'], 
            "user_id": user['id'], 
            "username": user['username']
        }
        access_token = create_access_token(token_data)
        
        user_response = UserResponse(
            id=user['id'],
            email=user['email'],
            username=user['username'],
            created_at=user['created_at'],
            last_login=user.get('last_login'),
            is_active=user.get('is_active', True)
        )
        
        logger.info(f"User logged in: {login_data.email}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile (protected)
    """
    return UserResponse(
        id=current_user["user_data"]["id"],
        email=current_user["user_data"]["email"],
        username=current_user["user_data"]["username"],
        created_at=current_user["user_data"]["created_at"],
        last_login=current_user["user_data"].get("last_login"),
        is_active=current_user["user_data"].get("is_active", True)
    )

@router.post("/refresh")
def refresh_token(authorization: str = Header(...)):
    """
    Refresh access token
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Create new access token
    new_access_token = create_access_token({
        "sub": payload.get("sub"),
        "user_id": payload.get("user_id"),
        "username": payload.get("username")
    })
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
def logout():
    """
    Logout user (client should remove token)
    """
    return {"message": "Successfully logged out"}

@router.get("/verify")
def verify_token_endpoint(authorization: str = Header(...)):
    """
    Verify token validity
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "valid": True,
        "user_id": payload.get("user_id"),
        "email": payload.get("sub"),
        "expires_in": payload.get("exp")
    }