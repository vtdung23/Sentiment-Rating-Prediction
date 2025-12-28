"""
Database Configuration and Session Management
Supports BOTH SQLite (local) and PostgreSQL (production on Render)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# ============================================
# HYBRID DATABASE SUPPORT
# ============================================
# Priority:
# 1. Use DATABASE_URL from environment (Render PostgreSQL)
# 2. Fallback to SQLite for local development

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # CRITICAL FIX FOR RENDER:
    # Render provides URLs starting with 'postgres://'
    # but SQLAlchemy 1.4+ requires 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    print(f"🚀 Production Mode: Using PostgreSQL")
    
    # PostgreSQL: No need for check_same_thread
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=300,    # Recycle connections every 5 minutes
    )
else:
    # Local development: Use SQLite
    print(f"🔧 Development Mode: Using SQLite")
    
    # Create database directory
    db_dir = Path("app/database")
    db_dir.mkdir(parents=True, exist_ok=True)
    
    DATABASE_URL = "sqlite:///./app/database/rating_prediction.db"
    
    # SQLite: Needs check_same_thread=False for FastAPI
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    """
    Dependency to get database session
    Used in FastAPI route dependencies
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
