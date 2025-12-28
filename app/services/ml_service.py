"""
ML Prediction Service with LAZY LOADING & REMOTE MODEL FETCHING
Enhanced with: SHAP Explanation, N-gram Analysis, Keyword Detection
"""
import os
import re
from typing import List, Dict, Any, Optional
from collections import Counter
# [QUAN TRỌNG] Import thư viện để tải model từ kho riêng
from huggingface_hub import hf_hub_download

# Only set HF cache for local development
# if not os.getenv("RENDER") and not os.getenv("SPACE_ID"):
#     os.environ['HF_HOME'] = 'G:/huggingface_cache'


class KeywordAnalyzer:
    """Analyzes text for positive/negative keywords"""
    
    def __init__(self):
        # Vietnamese positive keywords
        self.positive_words = [
            'tốt', 'đẹp', 'tuyệt vời', 'xuất sắc', 'hoàn hảo', 'chất lượng',
            'nhanh', 'tiện', 'ưng', 'hài lòng', 'thích', 'yêu', 'tuyệt',
            'ok', 'ổn', 'được', 'giỏi', 'hay', 'ngon', 'xịn', 'đỉnh',
            'pro', 'amazing', 'perfect', 'good', 'great', 'excellent',
            'rẻ', 'đáng tiền', 'đáng mua', 'recommend', 'khuyên', 'nên mua',
            'chính hãng', 'uy tín', 'nhiệt tình', 'chu đáo', 'cảm ơn',
            'giao nhanh', 'đóng gói cẩn thận', 'đúng mô tả', 'như hình',
            'rất tốt', 'rất đẹp', 'rất ưng', 'rất thích', 'siêu', 'quá đẹp'
        ]
        
        # Vietnamese negative keywords
        self.negative_words = [
            'tệ', 'xấu', 'kém', 'dở', 'tồi', 'thất vọng', 'chán',
            'chậm', 'lâu', 'lỗi', 'hỏng', 'vỡ', 'rách', 'bẩn',
            'giả', 'fake', 'lừa', 'đắt', 'không đáng', 'phí tiền',
            'bad', 'poor', 'terrible', 'awful', 'worst', 'horrible',
            'không thích', 'không ưng', 'không hài lòng', 'không như',
            'trả lại', 'hoàn tiền', 'không đúng', 'sai', 'thiếu',
            'giao chậm', 'đóng gói ẩu', 'móp', 'méo', 'cũ', 'rất tệ',
            'quá tệ', 'không tốt', 'không ok', 'dở ẹt', 'rất xấu'
        ]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text for positive/negative keywords"""
        text_lower = text.lower()
        
        found_positive = []
        found_negative = []
        
        for word in self.positive_words:
            if word.lower() in text_lower:
                found_positive.append(word)
        
        for word in self.negative_words:
            if word.lower() in text_lower:
                found_negative.append(word)
        
        return {
            'positive_keywords': found_positive,
            'negative_keywords': found_negative,
            'positive_count': len(found_positive),
            'negative_count': len(found_negative)
        }


class NgramAnalyzer:
    """Analyzes text for n-grams"""
    
    def __init__(self):
        # Vietnamese stopwords to exclude
        self.stopwords = set([
            'và', 'của', 'có', 'cho', 'với', 'từ', 'này', 'được',
            'là', 'để', 'một', 'các', 'trong', 'không', 'đã', 'rất',
            'cũng', 'nhưng', 'thì', 'bị', 'khi', 'nếu', 'như', 'về',
            'tôi', 'bạn', 'mình', 'nó', 'họ', 'em', 'anh', 'chị',
            'vì', 'nên', 'đến', 'lại', 'ra', 'đang', 'sẽ', 'đều',
            'hay', 'thế', 'làm', 'rồi', 'đó', 'ở', 'thấy', 'còn',
            'shop', 'sp', 'sản phẩm', 'hàng', 'đơn', 'giao'
        ])
    
    def extract_ngrams(self, texts: List[str], n: int = 2, top_k: int = 15) -> List[Dict[str, Any]]:
        """Extract top n-grams from list of texts"""
        all_ngrams = []
        
        for text in texts:
            # Tokenize
            words = self._tokenize(text)
            # Filter stopwords
            words = [w for w in words if w.lower() not in self.stopwords and len(w) > 1]
            
            # Generate n-grams
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                all_ngrams.append(ngram)
        
        # Count and get top k
        counter = Counter(all_ngrams)
        top_ngrams = counter.most_common(top_k)
        
        return [{'ngram': ngram, 'count': count} for ngram, count in top_ngrams]
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for Vietnamese"""
        # Remove special characters but keep Vietnamese diacritics
        text = re.sub(r'[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', ' ', text.lower())
        return text.split()
    
    def analyze_single(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze single text for unigrams, bigrams, trigrams"""
        return {
            'unigrams': self.extract_ngrams([text], n=1, top_k=10),
            'bigrams': self.extract_ngrams([text], n=2, top_k=10),
            'trigrams': self.extract_ngrams([text], n=3, top_k=10)
        }
    
    def analyze_batch(self, texts: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze batch of texts for n-grams"""
        return {
            'unigrams': self.extract_ngrams(texts, n=1, top_k=15),
            'bigrams': self.extract_ngrams(texts, n=2, top_k=15),
            'trigrams': self.extract_ngrams(texts, n=3, top_k=10)
        }


class MLPredictionService:
    """
    ML Service with lazy loading.
    Fetches heavy model weights from external Hugging Face Model Repo
    to bypass the 1GB limit of Space Git Repo.
    """

    def __init__(self):
        """Initialize service without loading model (lazy loading)"""
        # Model components
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None
        self.device: Optional[str] = None
        self.model_loaded = False
        
        # [SỬA ĐỔI] Không set đường dẫn cứng ở đây nữa vì file không còn ở máy
        # Chúng ta sẽ định nghĩa Repo ID chứa model ở đây
        self.MODEL_REPO_ID = "vtdung23/my-phobert-models"
        self.MODEL_FILENAME = "best_phoBER.pth"
        
        # Initialize analyzers
        self.keyword_analyzer = KeywordAnalyzer()
        self.ngram_analyzer = NgramAnalyzer()
        
        print("✅ ML Service initialized (Model will download & load on first request)")

    
    def _load_model(self):
        """Load model and tokenizer (called on first request)"""
        if self.model_loaded:
            return
        
        print("🔄 Loading ML model (first request)...")
        
        # Import heavy dependencies only when needed
        import torch
        from transformers import AutoTokenizer, RobertaForSequenceClassification
        
        # Determine device
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"📍 Using device: {self.device}")
        
        # [SỬA ĐỔI 1] Load Tokenizer từ gốc vinai/phobert-base
        # Vì folder tokenizer local đã bị xóa, ta load thẳng từ thư viện gốc cho an toàn
        print("📦 Loading tokenizer from vinai/phobert-base...")
        self.tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=False)
        
        # [SỬA ĐỔI 2] Tải file weights từ Kho Model riêng về
        print(f"⬇️ Downloading weights from repo: {self.MODEL_REPO_ID}...")
        try:
            model_path = hf_hub_download(
                repo_id=self.MODEL_REPO_ID,
                filename=self.MODEL_FILENAME,
                repo_type="model" # Quan trọng: báo đây là kho Model
            )
            print(f"✅ Downloaded weights to: {model_path}")
        except Exception as e:
            print(f"❌ Error downloading model: {e}")
            raise e

        # Load model architecture
        print("🧠 Loading PhoBERT architecture...")
        self.model = RobertaForSequenceClassification.from_pretrained(
            "vinai/phobert-base",
            num_labels=5, # Đảm bảo số này khớp với lúc bạn train (0,1,2,3,4 hay 1-5?)
            problem_type="single_label_classification"
        )
        
        # Load fine-tuned weights
        print("⚙️ Loading trained weights into architecture...")
        state_dict = torch.load(model_path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(state_dict)
        
        # Set to evaluation mode and move to device
        self.model.eval()
        self.model.to(self.device)
        
        self.model_loaded = True
        print("✅ Model loaded successfully and ready to serve!")
            
    def predict_single(self, text: str) -> Dict[str, Any]:
        """Predict rating for a single comment"""
        # Lazy load model on first request
        self._load_model()
        
        import torch
        import torch.nn.functional as F

        # 1. Vietnamese preprocessing
        processed_text = self.preprocess(text)

        # 2. Tokenize
        encoded = self.tokenizer(
            processed_text,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )
        
        # Move tensors to device
        encoded = {k: v.to(self.device) for k, v in encoded.items()}

        # 3. Inference
        with torch.no_grad():
            outputs = self.model(**encoded)
            logits = outputs.logits
            probs = F.softmax(logits, dim=1)

        # 4. Get prediction + confidence
        predicted_class = torch.argmax(probs, dim=1).item()
        confidence = probs[0][predicted_class].item()

        # 5. Convert 0-based label -> rating 1-5
        # (Giả sử model train label 0 tương ứng 1 sao)
        rating = predicted_class + 1

        return {
            'rating': rating,
            'confidence': confidence
        }
    
    def predict_with_explanation(self, text: str) -> Dict[str, Any]:
        """
        Predict rating with explanation (word importance scores)
        Uses gradient-based attribution for interpretability
        """
        # Lazy load model on first request
        self._load_model()
        
        import torch
        import torch.nn.functional as F
        
        # 1. Vietnamese preprocessing
        processed_text = self.preprocess(text)
        words = processed_text.split()
        
        # 2. Tokenize
        encoded = self.tokenizer(
            processed_text,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors="pt"
        )
        
        # Move tensors to device
        encoded = {k: v.to(self.device) for k, v in encoded.items()}
        
        # 3. Get embeddings and enable gradient computation
        embeddings = self.model.roberta.embeddings(encoded['input_ids'])
        embeddings.requires_grad_(True)
        
        # 4. Forward pass with embeddings
        with torch.enable_grad():
            outputs = self.model.roberta.encoder(embeddings)
            sequence_output = outputs.last_hidden_state
            logits = self.model.classifier(sequence_output)
            probs = F.softmax(logits, dim=1)
            
            # Get predicted class
            predicted_class = torch.argmax(probs, dim=1).item()
            confidence = probs[0][predicted_class].item()
            
            # Compute gradient for the predicted class
            target_score = probs[0][predicted_class]
            target_score.backward()
            
            # Get gradient-based importance
            gradients = embeddings.grad
            importance = gradients.abs().sum(dim=-1).squeeze()
        
        # 5. Map importance to words (simplified - using tokenizer alignment)
        tokens = self.tokenizer.convert_ids_to_tokens(encoded['input_ids'][0])
        token_importance = importance.detach().cpu().numpy()
        
        # Normalize importance scores
        if token_importance.max() > 0:
            token_importance = token_importance / token_importance.max()
        
        # Map to original words (simplified approach)
        word_importance = []
        for i, token in enumerate(tokens):
            if token not in ['<s>', '</s>', '<pad>']:
                # Assign positive/negative based on keyword analysis
                keyword_analysis = self.keyword_analyzer.analyze(token)
                base_score = float(token_importance[i])
                
                if keyword_analysis['positive_count'] > 0:
                    word_importance.append({
                        'word': token,
                        'score': base_score  # Positive contribution
                    })
                elif keyword_analysis['negative_count'] > 0:
                    word_importance.append({
                        'word': token,
                        'score': -base_score  # Negative contribution
                    })
                else:
                    word_importance.append({
                        'word': token,
                        'score': base_score * (0.5 if predicted_class >= 2 else -0.5)
                    })
        
        rating = predicted_class + 1
        
        # Also get keyword analysis for the full text
        keyword_analysis = self.keyword_analyzer.analyze(text)
        
        return {
            'rating': rating,
            'confidence': confidence,
            'explanation': {
                'words': [wi['word'] for wi in word_importance[:20]],
                'importance_scores': [wi['score'] for wi in word_importance[:20]],
                'overall_sentiment': 'positive' if rating >= 4 else ('negative' if rating <= 2 else 'neutral')
            },
            'keywords': keyword_analysis
        }
    
    def predict_batch(self, texts: List[str]) -> List[Dict[str, any]]:
        """Predict ratings for multiple comments"""
        results = []
        for text in texts:
            # Có thể tối ưu bằng cách batch tokenize, nhưng loop đơn giản cho an toàn
            prediction = self.predict_single(text)
            results.append({
                'text': text,
                'rating': prediction['rating'],
                'confidence': prediction['confidence']
            })
        return results
    
    def predict_batch_with_analysis(self, texts: List[str]) -> Dict[str, Any]:
        """
        Predict ratings for batch with additional analysis:
        - N-gram analysis
        - Keyword frequency
        - Rating distribution
        """
        # Get predictions
        predictions = self.predict_batch(texts)
        
        # N-gram analysis
        ngram_analysis = self.ngram_analyzer.analyze_batch(texts)
        
        # Aggregate keyword analysis
        all_positive = []
        all_negative = []
        for text in texts:
            kw = self.keyword_analyzer.analyze(text)
            all_positive.extend(kw['positive_keywords'])
            all_negative.extend(kw['negative_keywords'])
        
        positive_freq = Counter(all_positive).most_common(10)
        negative_freq = Counter(all_negative).most_common(10)
        
        return {
            'predictions': predictions,
            'ngrams': ngram_analysis,
            'keyword_frequency': {
                'positive': [{'word': w, 'count': c} for w, c in positive_freq],
                'negative': [{'word': w, 'count': c} for w, c in negative_freq]
            }
        }
    
    def analyze_ngrams(self, texts: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze n-grams for a list of texts"""
        return self.ngram_analyzer.analyze_batch(texts)
    
    def preprocess(self, text: str) -> str:
        """Preprocess Vietnamese text"""
        from underthesea import word_tokenize
        text = word_tokenize(text, format="text")
        return text

# Singleton instance
ml_service = MLPredictionService()

def get_ml_service() -> MLPredictionService:
    return ml_service