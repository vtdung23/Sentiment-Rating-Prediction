"""
Prediction Router
Handles single and batch predictions with enhanced features:
- Keyword highlighting
- SHAP/Interpretability explanation
- N-gram analysis
"""
import io
import csv
from typing import List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, PredictionHistory
from app.schemas import (
    SinglePredictionRequest,
    SinglePredictionResponse,
    BatchPredictionResponse,
    PredictionHistoryResponse,
    PDFReportRequest,
    NgramAnalysisRequest,
    NgramAnalysisResponse
)
from app.services.auth_service import get_current_user
from app.services.ml_service import get_ml_service, MLPredictionService
from app.services.visualization_service import get_viz_service, VisualizationService
from app.services.report_service import get_report_service, ReportService

router = APIRouter()


def highlight_text(text: str, positive_keywords: List[str], negative_keywords: List[str]) -> str:
    """Apply HTML highlighting to keywords in text"""
    highlighted = text
    
    # Sort by length (longer first) to avoid partial matches
    for word in sorted(negative_keywords, key=len, reverse=True):
        highlighted = highlighted.replace(
            word, 
            f'<span class="highlight-negative">{word}</span>'
        )
    
    for word in sorted(positive_keywords, key=len, reverse=True):
        highlighted = highlighted.replace(
            word, 
            f'<span class="highlight-positive">{word}</span>'
        )
    
    return highlighted


@router.post("/single", response_model=SinglePredictionResponse)
async def predict_single(
    request: SinglePredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ml_service: MLPredictionService = Depends(get_ml_service)
):
    """
    Predict rating for a single comment with optional explanation
    
    - **product_name**: Name of the product
    - **comment**: Vietnamese product review text
    - **include_explanation**: Whether to include SHAP-like explanation
    
    Returns predicted rating (1-5 stars) with confidence score,
    keyword highlighting, and optionally word importance explanation
    """
    # Check if explanation is requested
    if request.include_explanation:
        # Use enhanced prediction with explanation
        result = ml_service.predict_with_explanation(request.comment)
        prediction = {
            'rating': result['rating'],
            'confidence': result['confidence']
        }
        explanation = result.get('explanation')
        keywords = result.get('keywords')
    else:
        # Use standard prediction
        prediction = ml_service.predict_single(request.comment)
        # Still get keyword analysis for highlighting
        keywords = ml_service.keyword_analyzer.analyze(request.comment)
        explanation = None
    
    # Generate highlighted text
    highlighted_comment = highlight_text(
        request.comment,
        keywords.get('positive_keywords', []) if isinstance(keywords, dict) else keywords.positive_keywords if keywords else [],
        keywords.get('negative_keywords', []) if isinstance(keywords, dict) else keywords.negative_keywords if keywords else []
    )
    
    # Save to history
    history = PredictionHistory(
        user_id=current_user.id,
        product_name=request.product_name,
        comment=request.comment,
        predicted_rating=prediction['rating'],
        confidence_score=prediction['confidence'],
        prediction_type='single'
    )
    db.add(history)
    db.commit()
    
    return {
        "predicted_rating": prediction['rating'],
        "confidence_score": prediction['confidence'],
        "comment": request.comment,
        "highlighted_comment": highlighted_comment,
        "explanation": explanation,
        "keywords": keywords
    }


@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    product_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ml_service: MLPredictionService = Depends(get_ml_service),
    viz_service: VisualizationService = Depends(get_viz_service),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Predict ratings for batch of comments from CSV file with enhanced analysis
    
    - **product_name**: Name of the product
    - **file**: CSV file with 'Comment' column
    
    Returns predictions with:
    - Visualization data (wordcloud, distribution chart)
    - N-gram analysis (unigrams, bigrams, trigrams)
    - Keyword frequency analysis
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    try:
        # Read CSV file
        contents = await file.read()
        csv_file = io.StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(csv_file)
        
        # Check for Comment column
        if 'Comment' not in reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must contain 'Comment' column"
            )
        
        # Extract comments
        comments = []
        for row in reader:
            if row.get('Comment', '').strip():
                comments.append(row['Comment'].strip())
        
        if not comments:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid comments found in CSV"
            )
        
        # Make batch predictions with analysis
        batch_result = ml_service.predict_batch_with_analysis(comments)
        predictions = batch_result['predictions']
        ngrams = batch_result['ngrams']
        keyword_frequency = batch_result['keyword_frequency']

        final_product_name = product_name if product_name else "Unknown Product"

        # Save to history
        for pred in predictions:
            history = PredictionHistory(
                user_id=current_user.id,
                product_name=final_product_name,
                comment=pred['text'],
                predicted_rating=pred['rating'],
                confidence_score=pred['confidence'],
                prediction_type='batch'
            )
            db.add(history)
        db.commit()
        
        # Calculate rating distribution
        ratings = [p['rating'] for p in predictions]
        distribution = viz_service.calculate_rating_distribution(ratings)
        
        # Generate word cloud
        wordcloud_filename = f"wordcloud_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        wordcloud_url = viz_service.generate_wordcloud(comments, wordcloud_filename)
        
        # Prepare results for CSV download
        results = []
        for pred in predictions:
            results.append({
                'Comment': pred['text'],
                'Predicted_Rating': pred['rating'],
                'Confidence': pred['confidence']
            })
        
        # Generate PDF report
        pdf_filename = f"report_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_content = report_service.generate_pdf_report(
            predictions=predictions,
            distribution=distribution,
            wordcloud_path=wordcloud_url,
            username=current_user.username,
            filename=pdf_filename
        )
        
        return {
            "total_predictions": len(predictions),
            "rating_distribution": distribution,
            "wordcloud_url": wordcloud_url,
            "results": results,
            "csv_download_url": f"/api/predict/download/{current_user.id}/{datetime.now().timestamp()}",
            "pdf_download_url": f"/api/predict/download-pdf/{current_user.id}/{datetime.now().timestamp()}",
            "ngrams": ngrams,
            "keyword_frequency": keyword_frequency
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )


@router.get("/history", response_model=List[PredictionHistoryResponse])
async def get_prediction_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get prediction history for current user
    
    - **limit**: Maximum number of records to return (default: 50)
    """
    history = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == current_user.id
    ).order_by(PredictionHistory.created_at.desc()).limit(limit).all()
    
    return history


@router.post("/download-csv")
async def download_predictions_csv(
    results: List[dict],
    current_user: User = Depends(get_current_user)
):
    """
    Download prediction results as CSV
    """
    # Create CSV in memory
    output = io.StringIO()
    
    if results:
        fieldnames = results[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    # Reset position
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


@router.post("/download-pdf")
async def download_predictions_pdf(
    request: PDFReportRequest,
    current_user: User = Depends(get_current_user),
    report_service: ReportService = Depends(get_report_service)
):
    """
    Download prediction results as PDF report
    """
    try:
        pdf_content = report_service.generate_pdf_report(
            predictions=request.predictions,
            distribution=request.distribution,
            wordcloud_path=request.wordcloud_path,
            username=current_user.username
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=predictions_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )


@router.post("/analyze-ngrams", response_model=NgramAnalysisResponse)
async def analyze_ngrams(
    request: NgramAnalysisRequest,
    current_user: User = Depends(get_current_user),
    ml_service: MLPredictionService = Depends(get_ml_service)
):
    """
    Analyze n-grams (unigrams, bigrams, trigrams) for a list of texts
    
    - **texts**: List of Vietnamese text comments
    
    Returns frequency analysis of word patterns
    """
    if not request.texts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No texts provided for analysis"
        )
    
    ngrams = ml_service.analyze_ngrams(request.texts)
    
    return ngrams


@router.post("/explain")
async def explain_prediction(
    request: SinglePredictionRequest,
    current_user: User = Depends(get_current_user),
    ml_service: MLPredictionService = Depends(get_ml_service)
):
    """
    Get detailed explanation for a prediction
    
    Returns word importance scores and keyword analysis
    """
    result = ml_service.predict_with_explanation(request.comment)
    
    return {
        "predicted_rating": result['rating'],
        "confidence_score": result['confidence'],
        "comment": request.comment,
        "explanation": result['explanation'],
        "keywords": result['keywords']
    }
