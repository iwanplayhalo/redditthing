"""Ticker extraction and validation utilities"""

import re
import time
import yfinance as yf
from typing import List

class TickerExtractor:
    """Extracts and validates stock tickers from text"""
    
    def __init__(self, validation_delay: float = 0.2):
        self.validation_delay = validation_delay
        # Only pattern we need - $ followed by 1-5 uppercase letters
        self.dollar_ticker_pattern = re.compile(r'\$([A-Z]{1,5})\b')
    
    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol corresponds to a real stock
        
        Args:
            ticker: Potential ticker symbol
            
        Returns:
            True if valid ticker, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or len(info) <= 1:
                return False
            
            required_fields = ['symbol', 'longName', 'regularMarketPrice']
            has_required = any(field in info for field in required_fields)
            
            hist = stock.history(period="5d")
            has_price_data = not hist.empty
            
            return has_required and has_price_data
            
        except Exception:
            return False
    
    def extract_tickers_from_text(self, text: str) -> List[str]:
        """
        Extract stock tickers that follow $ symbol (e.g., $AAPL, $TSLA)
        
        Args:
            text: Text to analyze
            
        Returns:
            List of validated ticker symbols
        """
        validated_tickers = set()
        
        # Only look for $TICKER format
        dollar_tickers = self.dollar_ticker_pattern.findall(text.upper())
        
        if not dollar_tickers:
            print(f"  No $TICKER format found in text")
            return []
        
        # Remove duplicates
        unique_tickers = list(set(dollar_tickers))
        print(f"  Found {len(unique_tickers)} tickers with $ prefix: {unique_tickers}")
        
        # Validate each ticker
        for ticker in unique_tickers:
            print(f"    Validating ${ticker}...", end=" ")
            if self.validate_ticker(ticker):
                validated_tickers.add(ticker)
                print("✓ Valid")
            else:
                print("✗ Invalid")
            time.sleep(self.validation_delay)
        
        return list(validated_tickers)