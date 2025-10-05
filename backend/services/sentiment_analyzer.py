from transformers import pipeline
from backend.models.data_models import SentimentScore
import nltk
from nltk.tokenize import sent_tokenize
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
nltk.download('punkt')

class SentimentAnalyzer:
    def __init__(self):
        try:
            self.analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
            logger.debug("Sentiment analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing sentiment analyzer: {str(e)}")
            raise

    def analyze_text(self, text: str, product: str = None, timestamp: datetime = None) -> Dict:
        try:
            logger.debug("Starting sentiment analysis")
            if not text:
                raise ValueError("Empty text provided for analysis")

            sentences = sent_tokenize(text)
            logger.debug(f"Tokenized {len(sentences)} sentences")

            results = self.analyzer(sentences)
            
            total = len(results)
            if total == 0:
                return {
                    "sentiment": SentimentScore(
                        positive=0.0, 
                        negative=0.0, 
                        neutral=1.0
                    ),
                    "justification": [],
                    "timestamp": timestamp
                }

            # Calculate scores
            positive = sum(1 for r in results if int(r['label'][0]) >= 4) / total
            negative = sum(1 for r in results if int(r['label'][0]) <= 2) / total
            neutral = sum(1 for r in results if int(r['label'][0]) == 3) / total

            scores = {
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'compound': (positive - negative)  # Simple compound calculation
            }

            logger.debug(f"Analysis complete with scores: {scores}")
            
            return {
                "sentiment": SentimentScore(**scores),
                "justification": self._get_justifications(sentences, results),
                "timestamp": timestamp
            }

        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}", exc_info=True)
            raise

    def _get_justifications(self, sentences: List[str], results: List[Dict]) -> List[Tuple[str, float]]:
        """Extract sentences that strongly support the sentiment"""
        try:
            sentence_scores = []
            for sentence, result in zip(sentences, results):
                score = int(result['label'][0]) / 5.0
                if len(sentence.split()) >= 5:
                    sentence_scores.append((sentence, score))
            return sorted(sentence_scores, key=lambda x: abs(x[1] - 0.5), reverse=True)
        except Exception as e:
            logger.error(f"Error getting justifications: {str(e)}")
            return []