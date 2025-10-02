"""Configuration settings for the Reddit stocks analyzer"""
import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    """Configuration class for API credentials and settings"""
    
    # Reddit API credentials
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "RedditStockAnalyzer")
    
    # Subreddit settings
    SUBREDDIT_NAME = os.getenv("SUBREDDIT_NAME", "pennystocks")
    
    # Database settings
    DATABASE_NAME = os.getenv("DATABASE_NAME", "reddit_stocks.db")
    
    # Analysis settings
    DEFAULT_POST_LIMIT = int(os.getenv("DEFAULT_POST_LIMIT", "100"))
    TIME_PERIODS = [
        (1, 'return_1d', 'price_1d'),
        (3, 'return_3d', 'price_3d'),
        (7, 'return_1w', 'price_1w'),
        (14, 'return_2w', 'price_2w'),
        (30, 'return_1m', 'price_1m')
    ]
    
    # API rate limiting
    YAHOO_FINANCE_DELAY = 0.1  # Seconds between requests
    TICKER_VALIDATION_DELAY = 0.2  # Seconds between ticker validations