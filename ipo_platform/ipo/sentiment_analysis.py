"""
Sentiment Analysis Module
Analyzes news and social media sentiment for IPOs.
"""

import requests
import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    symbol: str
    overall_sentiment: str  # 'positive', 'negative', 'neutral'
    sentiment_score: float  # -1 to 1
    confidence: float  # 0 to 1
    positive_count: int
    negative_count: int
    neutral_count: int
    key_topics: List[str]
    news_count: int
    last_updated: datetime


class SentimentAnalyzer:
    """
    Analyzes sentiment from news articles and social media.
    """
    
    # Sentiment word dictionaries
    POSITIVE_WORDS = {
        'growth', 'profit', 'success', 'gain', 'strong', 'bullish', 'promising',
        'opportunity', 'innovation', 'leader', 'expansion', 'record', 'beat',
        'surge', 'rally', 'breakthrough', 'partnership', 'award', 'top', 'best',
        'excellent', 'outstanding', 'robust', 'resilient', 'upgrade', 'buy',
        'recommend', 'attractive', 'undervalued', 'dividend', 'earnings', 'revenue'
    }
    
    NEGATIVE_WORDS = {
        'loss', 'decline', 'fall', 'drop', 'risk', 'concern', 'uncertainty',
        'lawsuit', 'investigation', 'scandal', 'layoff', 'cut', 'warning',
        'miss', 'weak', 'bearish', 'volatile', 'trouble', 'debt', 'default',
        'downgrade', 'sell', 'overvalued', 'warning', 'risk', 'threat', 'challenge',
        'slowdown', 'recession', 'uncertain', 'volatile', 'down', 'fail', 'loss'
    }
    
    NEUTRAL_WORDS = {
        'report', 'announce', 'state', 'say', 'according', 'market', 'company',
        'stock', 'price', 'share', 'data', 'index', 'quarter', 'year', 'period'
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize sentiment analyzer.
        
        Args:
            api_key: NewsAPI key (optional)
        """
        self.api_key = api_key
        self.cache = {}
        self.cache_duration = 3600  # 1 hour
    
    def analyze_sentiment(self, symbol: str, company_name: str = None) -> SentimentResult:
        """
        Analyze sentiment for a given symbol.
        
        Args:
            symbol: Stock symbol
            company_name: Full company name for better search
            
        Returns:
            SentimentResult with analysis
        """
        # Check cache
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H')}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_duration:
                return cached['result']
        
        # Fetch news articles
        news_articles = self._fetch_news(symbol, company_name)
        
        # Analyze each article
        sentiment_results = []
        for article in news_articles:
            sentiment = self._analyze_text(article.get('title', '') + ' ' + article.get('description', ''))
            sentiment_results.append(sentiment)
        
        # Aggregate results
        if sentiment_results:
            avg_score = sum(s['score'] for s in sentiment_results) / len(sentiment_results)
            positive_count = sum(1 for s in sentiment_results if s['label'] == 'positive')
            negative_count = sum(1 for s in sentiment_results if s['label'] == 'negative')
            neutral_count = sum(1 for s in sentiment_results if s['label'] == 'neutral')
            
            # Get key topics
            all_topics = []
            for s in sentiment_results:
                all_topics.extend(s.get('topics', []))
            key_topics = Counter(all_topics).most_common(5)
            key_topics = [t[0] for t in key_topics]
        else:
            avg_score = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            key_topics = []
        
        # Determine overall sentiment
        if avg_score > 0.1:
            overall = 'positive'
        elif avg_score < -0.1:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        # Calculate confidence
        total = positive_count + negative_count + neutral_count
        confidence = min(1.0, total / 10) if total > 0 else 0
        
        result = SentimentResult(
            symbol=symbol,
            overall_sentiment=overall,
            sentiment_score=round(avg_score, 3),
            confidence=round(confidence, 2),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count,
            key_topics=key_topics,
            news_count=len(news_articles),
            last_updated=datetime.now()
        )
        
        # Cache result
        self.cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        return result
    
    def _fetch_news(self, symbol: str, company_name: str = None) -> List[Dict]:
        """
        Fetch news articles for the symbol.
        """
        articles = []
        
        # Try NewsAPI if key is available
        if self.api_key:
            try:
                url = 'https://newsapi.org/v2/everything'
                params = {
                    'q': f'{symbol} OR {company_name or symbol}',
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 20,
                    'apiKey': self.api_key
                }
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = [{'title': a.get('title', ''), 'description': a.get('description', '')} 
                               for a in data.get('articles', [])]
            except Exception as e:
                logger.error(f"Error fetching news: {e}")
        
        # If no API or failed, use mock data for demonstration
        if not articles:
            articles = self._get_mock_news(symbol)
        
        return articles
    
    def _get_mock_news(self, symbol: str) -> List[Dict]:
        """
        Generate mock news for demonstration when API is not available.
        """
        import random
        
        templates = [
            {
                'title': f'{symbol} Reports Strong Quarterly Earnings',
                'description': f'{symbol} beats analyst expectations with record revenue growth.'
            },
            {
                'title': f'{symbol} Announces New Partnership',
                'description': f'{symbol} expands market reach through strategic partnership.'
            },
            {
                'title': f'Analysts Upgrade {symbol} Rating',
                'description': f'Wall Street firms raise price targets for {symbol} stock.'
            },
            {
                'title': f'{symbol} Faces Market Volatility',
                'description': f'{symbol} experiences short-term price fluctuations amid broader market uncertainty.'
            },
            {
                'title': f'{symbol} CEO Discusses Growth Strategy',
                'description': f'Leadership outlines plans for expansion and innovation.'
            }
        ]
        
        # Randomly select and modify templates
        selected = random.sample(templates, min(3, len(templates)))
        return selected
    
    def _analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        if not text:
            return {'score': 0, 'label': 'neutral', 'topics': []}
        
        # Tokenize and clean
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Count sentiment words
        positive_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)
        neutral_count = sum(1 for w in words if w in self.NEUTRAL_WORDS)
        
        # Extract topics
        topics = self._extract_topics(words)
        
        # Calculate score
        total = positive_count + negative_count + neutral_count
        if total == 0:
            score = 0
        else:
            score = (positive_count - negative_count) / total
        
        # Determine label
        if score > 0.1:
            label = 'positive'
        elif score < -0.1:
            label = 'negative'
        else:
            label = 'neutral'
        
        return {
            'score': score,
            'label': label,
            'topics': topics
        }
    
    def _extract_topics(self, words: List[str]) -> List[str]:
        """
        Extract key topics from word list.
        """
        topics = []
        topic_keywords = {
            'earnings': ['earnings', 'revenue', 'profit', 'income', 'quarter'],
            'growth': ['growth', 'expand', 'increase', 'rise', 'gain'],
            'innovation': ['innovation', 'technology', 'product', 'launch', '研发'],
            'market': ['market', 'stock', 'share', 'price', 'trading'],
            'management': ['ceo', 'leadership', 'board', 'executive', 'strategy'],
            'partnership': ['partnership', 'deal', 'acquisition', 'merge', 'collaboration']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in words for kw in keywords):
                topics.append(topic)
        
        return topics
    
    def get_sentiment_trend(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        Get sentiment trend over time.
        
        Args:
            symbol: Stock symbol
            days: Number of days to analyze
            
        Returns:
            List of daily sentiment data
        """
        trend = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # For demo, simulate varying sentiment
            import random
            base_score = 0.1 if random.random() > 0.3 else -0.1
            score = base_score + random.uniform(-0.2, 0.2)
            score = max(-1, min(1, score))
            
            trend.append({
                'date': date_str,
                'sentiment_score': round(score, 3),
                'label': 'positive' if score > 0.1 else ('negative' if score < -0.1 else 'neutral'),
                'articles': random.randint(2, 15)
            })
        
        return trend
    
    def compare_sentiment(self, symbols: List[str]) -> Dict[str, SentimentResult]:
        """
        Compare sentiment across multiple symbols.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to SentimentResult
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.analyze_sentiment(symbol)
        return results
    
    def get_market_sentiment_index(self) -> Dict:
        """
        Get overall market sentiment index.
        """
        # Sample of major indices/sectors for market sentiment
        market_symbols = ['NIFTY', 'SENSEX', 'NASDAQ', 'SPY']
        
        sentiments = []
        for symbol in market_symbols:
            result = self.analyze_sentiment(symbol)
            sentiments.append(result.sentiment_score)
        
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            if avg_sentiment > 0.15:
                market_mood = 'Bullish'
            elif avg_sentiment < -0.15:
                market_mood = 'Bearish'
            else:
                market_mood = 'Neutral'
            
            return {
                'market_mood': market_mood,
                'sentiment_index': round(avg_sentiment, 3),
                'interpretation': self._interpret_market_sentiment(avg_sentiment),
                'symbols_analyzed': len(market_symbols)
            }
        
        return {
            'market_mood': 'Unknown',
            'sentiment_index': 0,
            'interpretation': 'Insufficient data',
            'symbols_analyzed': 0
        }
    
    def _interpret_market_sentiment(self, score: float) -> str:
        """Interpret market sentiment score."""
        if score > 0.5:
            return "Strong bullish sentiment across markets"
        elif score > 0.2:
            return "Moderate optimism prevailing"
        elif score > 0:
            return "Slight positive bias"
        elif score > -0.2:
            return "Slight negative bias"
        elif score > -0.5:
            return "Moderate pessimism prevailing"
        else:
            return "Strong bearish sentiment across markets"


class SocialMediaAnalyzer:
    """
    Analyze sentiment from social media platforms.
    """
    
    def __init__(self):
        self.platforms = ['twitter', 'reddit', 'stocktwits']
    
    def analyze_social_sentiment(self, symbol: str) -> Dict:
        """
        Analyze social media sentiment for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with social sentiment analysis
        """
        # For demo purposes, return simulated data
        import random
        
        total_posts = random.randint(50, 500)
        bullish = random.randint(20, int(total_posts * 0.6))
        bearish = random.randint(10, int(total_posts * 0.3))
        neutral = total_posts - bullish - bearish
        
        return {
            'symbol': symbol,
            'total_posts': total_posts,
            'bullish_posts': bullish,
            'bearish_posts': bearish,
            'neutral_posts': neutral,
            'bullish_ratio': round(bullish / total_posts, 2),
            'bearish_ratio': round(bearish / total_posts, 2),
            'sentiment_score': round((bullish - bearish) / total_posts, 3),
            'social_buzz': random.randint(1, 10),
            'top_discussion_topics': self._get_top_topics()
        }
    
    def _get_top_topics(self) -> List[str]:
        """Get top discussion topics."""
        topics = [
            'Earnings Report',
            'Product Launch',
            'Market Conditions',
            'Analyst Ratings',
            'Sector Trends'
        ]
        import random
        return random.sample(topics, 3)
    
    def get_trending_symbols(self) -> List[Dict]:
        """
        Get trending symbols on social media.
        """
        # Mock trending data
        trending = [
            {'symbol': 'NVDA', 'mentions': 5000, 'sentiment': 0.3},
            {'symbol': 'TSLA', 'mentions': 4500, 'sentiment': 0.1},
            {'symbol': 'AAPL', 'mentions': 4000, 'sentiment': 0.2},
            {'symbol': 'AMD', 'mentions': 3500, 'sentiment': 0.25},
            {'symbol': 'MSFT', 'mentions': 3000, 'sentiment': 0.15}
        ]
        return trending


def calculate_sentiment_impact(recommendation: Dict, sentiment: SentimentResult) -> Dict:
    """
    Calculate how sentiment affects investment recommendation.
    
    Args:
        recommendation: Existing recommendation data
        sentiment: Sentiment analysis result
        
    Returns:
        Updated recommendation with sentiment impact
    """
    # Adjust score based on sentiment
    sentiment_factor = sentiment.sentiment_score * 0.15  # Sentiment can adjust up to 15%
    
    adjusted_score = recommendation.get('overall_score', 50) + sentiment_factor * 50
    adjusted_score = min(100, max(0, adjusted_score))
    
    # Update rating if sentiment is strong
    current_rating = recommendation.get('rating', 'HOLD')
    if sentiment.confidence > 0.5:
        if sentiment.sentiment_score > 0.3 and current_rating in ['HOLD', 'BUY']:
            rating = 'STRONG_BUY' if current_rating == 'BUY' else 'BUY'
        elif sentiment.sentiment_score < -0.3 and current_rating in ['HOLD', 'BUY']:
            rating = 'SELL'
        else:
            rating = current_rating
    else:
        rating = current_rating
    
    return {
        **recommendation,
        'overall_score': round(adjusted_score, 1),
        'rating': rating,
        'sentiment_score': sentiment.sentiment_score,
        'sentiment_confidence': sentiment.confidence,
        'sentiment_label': sentiment.overall_sentiment,
        'sentiment_topics': sentiment.key_topics,
        'sentiment_adjusted': True
    }

