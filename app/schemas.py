"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# ===== Auth Schemas =====
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None


# ===== Prediction Schemas =====
class SinglePredictionRequest(BaseModel):
    product_name: Optional[str] = ""
    comment: str
    include_explanation: Optional[bool] = False

class ExplanationData(BaseModel):
    words: List[str]
    importance_scores: List[float]
    overall_sentiment: str

class KeywordData(BaseModel):
    positive_keywords: List[str]
    negative_keywords: List[str]
    positive_count: int
    negative_count: int

class SinglePredictionResponse(BaseModel):
    predicted_rating: int
    confidence_score: float
    comment: str
    highlighted_comment: Optional[str] = None
    explanation: Optional[ExplanationData] = None
    keywords: Optional[KeywordData] = None

class NgramItem(BaseModel):
    ngram: str
    count: int

class NgramAnalysis(BaseModel):
    unigrams: List[NgramItem]
    bigrams: List[NgramItem]
    trigrams: List[NgramItem]

class KeywordFrequencyItem(BaseModel):
    word: str
    count: int

class KeywordFrequency(BaseModel):
    positive: List[KeywordFrequencyItem]
    negative: List[KeywordFrequencyItem]

class BatchPredictionResponse(BaseModel):
    total_predictions: int
    rating_distribution: dict
    wordcloud_url: str
    results: List[dict]
    csv_download_url: str
    pdf_download_url: str
    ngrams: Optional[NgramAnalysis] = None
    keyword_frequency: Optional[KeywordFrequency] = None

class PDFReportRequest(BaseModel):
    predictions: List[dict]
    distribution: dict
    wordcloud_path: str


# ===== History Schemas =====
class PredictionHistoryResponse(BaseModel):
    id: int
    product_name: str
    comment: str
    predicted_rating: int
    confidence_score: Optional[float]
    prediction_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ===== Analysis Schemas =====
class NgramAnalysisRequest(BaseModel):
    texts: List[str]
    
class NgramAnalysisResponse(BaseModel):
    unigrams: List[NgramItem]
    bigrams: List[NgramItem]
    trigrams: List[NgramItem]
