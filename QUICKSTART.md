# 🚀 Quick Start Guide

## Installation

1. **Tạo môi trường ảo (Virtual Environment):**

   **Option A - Dùng Conda:**
   ```bash
   conda create -p ./env python=3.10 -y
   conda activate ./env
   ```

   **Option B - Dùng venv:**
   ```bash
   python -m venv env
   # Windows:
   env\Scripts\activate
   # Linux/Mac:
   source env/bin/activate
   ```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

4. **Access the application:**
- Dashboard: http://localhost:8000
- **Swagger API Docs: http://localhost:8000/docs** ⭐ (Show this to your teacher!)
- ReDoc: http://localhost:8000/redoc

## First Time Usage

1. Go to http://localhost:8000/login
2. Click "Register here" and create an account
3. Login with your credentials
4. You'll be redirected to the dashboard

## Testing Single Prediction

1. Select a product from dropdown
2. Click "Single Comment" tab
3. Enter a Vietnamese comment like: "Sản phẩm rất tốt, chất lượng cao, đóng gói cẩn thận"
4. Click "Predict Rating"
5. See the result with rating and confidence

## Testing Batch Prediction (CSV)

1. Create a CSV file with this format:
```csv
Comment
"Sản phẩm rất tốt, đóng gói cẩn thận"
"Chất lượng kém, không như mô tả"
"Giao hàng nhanh, sản phẩm ổn"
"Rất hài lòng với sản phẩm này"
"Giá hơi cao nhưng chất lượng tốt"
```

2. Select a product
3. Click "Upload CSV" tab
4. Upload your CSV file
5. Click "Predict Batch"
6. View:
   - Bar chart showing rating distribution
   - Word cloud of common words
   - Full results table
   - Download CSV with predictions

## Swagger UI Demo (For Teacher)

1. Open http://localhost:8000/docs
2. Show the endpoints:
   - Authentication (register, login)
   - Predictions (single, batch)
   - History
3. Click "Try it out" to test any endpoint
4. Show the automatic request/response documentation

## Replace Dummy ML Model

Edit `app/services/ml_service.py`:

```python
def __init__(self):
    # Load your real model here
    self.model = load_model('path/to/your/model')
    self.tokenizer = load_tokenizer('path/to/tokenizer')

def predict_single(self, text: str) -> Dict[str, any]:
    # Your preprocessing
    preprocessed = self.preprocess(text)
    
    # Your prediction
    prediction = self.model.predict(preprocessed)
    rating = int(prediction)  # Convert to 1-5
    
    return {
        'rating': rating,
        'confidence': float(prediction_confidence)
    }
```

## Troubleshooting

**"Module not found":**
```bash
pip install -r requirements.txt
```

**"Port already in use":**
Edit `main.py` and change port 8000 to another number.

**"Database locked":**
Close any other instances of the app and restart.

## Project Highlights for Presentation

✅ **FastAPI with automatic Swagger UI** (bonus points!)  
✅ **JWT Authentication** (secure login)  
✅ **RESTful API design** (professional structure)  
✅ **Data Visualization** (charts + word clouds)  
✅ **Batch Processing** (CSV upload/download)  
✅ **Responsive UI** (TailwindCSS)  
✅ **Database Integration** (SQLite with history tracking)  


Push lên GitHub: git push github main
Push lên Hugging Face: git push origin main
Push cả 2: git push github main && git push origin main

Good luck! 🎓
