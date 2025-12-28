"""
Configuration Settings
Supports environment variables for production deployment
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY (Environment-aware)
# ============================================
# In production (Render), set SECRET_KEY as environment variable
# Fallback to default for local development
SECRET_KEY = os.getenv(
    "SECRET_KEY", 
    "your-secret-key-change-in-production-2024-dev-only"
)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ============================================
# UPLOAD DIRECTORIES
# ============================================
# For production on Render, these will be in ephemeral storage
# Consider using cloud storage (S3, Cloudinary) for persistent files
UPLOAD_DIR = BASE_DIR / "app" / "static" / "uploads"
WORDCLOUD_DIR = UPLOAD_DIR / "wordclouds"

# Create directories if they don't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
WORDCLOUD_DIR.mkdir(parents=True, exist_ok=True)

# ============================================
# PRODUCTION SETTINGS
# ============================================
# Detect if running on Render (or any production environment)
IS_PRODUCTION = os.getenv("RENDER") is not None or os.getenv("DATABASE_URL") is not None

if IS_PRODUCTION:
    print("🚀 Running in PRODUCTION mode")
else:
    print("🔧 Running in DEVELOPMENT mode")

