"""
Visualization Service
WordCloud generation and data visualization utilities
"""
import os
from typing import List, Dict
from collections import Counter
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

from app.config import WORDCLOUD_DIR


class VisualizationService:
    """Service for generating visualizations"""
    
    def __init__(self):
        # Vietnamese stopwords (common words to exclude)
        self.stopwords = set([
            'và', 'của', 'có', 'cho', 'với', 'từ', 'này', 'được',
            'là', 'để', 'một', 'các', 'trong', 'không', 'đã', 'rất',
            'cũng', 'nhưng', 'thì', 'bị', 'khi', 'nếu', 'như', 'về',
            'tôi', 'bạn', 'mình', 'nó', 'họ', 'em', 'anh', 'chị',
            'vì', 'nên', 'đến', 'lại', 'ra', 'đang', 'sẽ', 'đều',
            'hay', 'thế', 'làm', 'được', 'rồi', 'đó', 'này', 'ở'
        ])
    
    def generate_wordcloud(self, texts: List[str], filename: str = None) -> str:
        """
        Generate word cloud from list of texts
        
        Args:
            texts: List of Vietnamese comments
            filename: Optional custom filename
            
        Returns:
            str: Path to generated word cloud image
        """
        # Combine all texts
        combined_text = ' '.join(texts)
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wordcloud_{timestamp}.png"
        
        filepath = WORDCLOUD_DIR / filename
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=self.stopwords,
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(combined_text)
        
        # Save to file
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Return relative URL path
        return f"/static/uploads/wordclouds/{filename}"
    
    def calculate_rating_distribution(self, ratings: List[int]) -> Dict[int, int]:
        """
        Calculate distribution of ratings
        
        Args:
            ratings: List of ratings (1-5)
            
        Returns:
            dict: {rating: count}
        """
        distribution = Counter(ratings)
        
        # Ensure all ratings 1-5 are present
        for rating in range(1, 6):
            if rating not in distribution:
                distribution[rating] = 0
        
        return dict(sorted(distribution.items()))
    
    def get_top_words(self, texts: List[str], top_n: int = 20) -> List[tuple]:
        """
        Get most frequent words from texts
        
        Args:
            texts: List of comments
            top_n: Number of top words to return
            
        Returns:
            list: [(word, count), ...]
        """
        # Combine and split texts
        words = []
        for text in texts:
            words.extend(text.lower().split())
        
        # Filter stopwords
        filtered_words = [w for w in words if w not in self.stopwords and len(w) > 2]
        
        # Count and return top words
        word_counts = Counter(filtered_words)
        return word_counts.most_common(top_n)


# Singleton instance
viz_service = VisualizationService()


def get_viz_service() -> VisualizationService:
    """Dependency to get visualization service"""
    return viz_service
