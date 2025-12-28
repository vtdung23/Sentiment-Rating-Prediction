"""
SQLAlchemy Database Models
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    predictions = relationship("PredictionHistory", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class PredictionHistory(Base):
    """Prediction history model"""
    __tablename__ = "prediction_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_name = Column(String(200), nullable=False)
    comment = Column(Text, nullable=False)
    predicted_rating = Column(Integer, nullable=False)
    confidence_score = Column(Float, nullable=True)
    prediction_type = Column(String(20), default="single")  # 'single' or 'batch'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="predictions")
    
    def __repr__(self):
        return f"<PredictionHistory {self.id}: {self.predicted_rating}⭐>"
