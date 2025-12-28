"""
Main FastAPI Application
Sentiment Rating Prediction System
"""
import os

# OPTIONAL: Set HuggingFace cache directory (only for local dev)
# Comment this out for production to use default cache
# if not os.getenv("RENDER"):  # Only for local development
#     os.environ['HF_HOME'] = 'G:/huggingface_cache'

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import engine, Base
from app.routers import auth, prediction, dashboard

# ============================================
# DATABASE AUTO-MIGRATION
# ============================================
# This creates all tables automatically on first deploy
# Critical for PostgreSQL on Render (no manual migrations needed)
print("🔄 Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")

# ============================================
# INITIALIZE FASTAPI APP
# ============================================
app = FastAPI(
    title="Vietnamese Product Rating Prediction API",
    description="ML-powered sentiment analysis for Vietnamese product reviews (1-5 stars)",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# ============================================
# CORS MIDDLEWARE
# ============================================
# For production, restrict origins to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# STATIC FILES & TEMPLATES
# ============================================
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ============================================
# INCLUDE ROUTERS
# ============================================
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(prediction.router, prefix="/api/predict", tags=["Prediction"])
app.include_router(dashboard.router, tags=["Dashboard"])

# ============================================
# ROOT & HEALTH CHECK ENDPOINTS
# ============================================
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Vietnamese Product Rating Prediction API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "rating-prediction",
        "version": "1.0.0"
    }

# ============================================
# LOCAL DEVELOPMENT SERVER
# ============================================
if __name__ == "__main__":
    # This only runs when executing: python main.py
    # On Render, gunicorn/uvicorn will be used instead
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
