# app/main.py
"""
PostGenerator Backend - FastAPI Application
Main entry point with authentication
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import auth routers
from auth.login import router as login_router
from auth.signup import router as signup_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PostGenerator API",
    description="AI-Powered Social Media Poster Generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4200", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routers
app.include_router(login_router, prefix="/auth", tags=["Authentication"])
app.include_router(signup_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {
        "message": "🚀 PostGenerator API is running!",
        "status": "active", 
        "version": "1.0.0",
        "services": ["authentication", "poster-generation"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from database.connection import test_connection
    
    db_status = "connected" if test_connection() else "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "authentication": "active",
        "ai_service": "ready"
    }

@app.get("/test-auth")
async def test_auth_protected(user: dict = Depends(get_current_user)):
    """
    Test protected route - requires authentication
    """
    return {
        "message": "✅ You have access to protected route!",
        "user": user
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )