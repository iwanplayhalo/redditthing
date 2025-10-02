"""Stock performance analysis using Yahoo Finance"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import List, Optional
from models import StockMention, StockPerformance
from config import Config

class StockAnalyzer:
    """Analyzes stock performance over time"""
    
    def __init__(self):
        self.time_periods = Config.TIME_PERIODS
        self.api_delay = Config.YAHOO_FINANCE_DELAY
    
    def get_stock_data(self, ticker: str, start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(start=start_date, end=end_date)
            
            if data.empty:
                return None
                
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None
    
    def calculate_performance(self, mentions: List[StockMention]) -> List[StockPerformance]:
        """Calculate stock performance for each mention"""
        performances = []
        processed_pairs = set()
        
        for mention in mentions:
            pair_key = (mention.ticker, mention.post_date.date())
            if pair_key in processed_pairs:
                continue
            processed_pairs.add(pair_key)
            
            start_date = mention.post_date.date() - timedelta(days=1)
            end_date = mention.post_date.date() + timedelta(days=35)
            
            print(f"Analyzing {mention.ticker} from post on {mention.post_date.date()}")
            
            stock_data = self.get_stock_data(mention.ticker, start_date, end_date)
            
            if stock_data is None or stock_data.empty:
                print(f"No data available for {mention.ticker}")
                continue
            
            try:
                post_date = mention.post_date.date()
                available_dates = stock_data.index.date
                
                post_price_date = None
                for date in available_dates:
                    if date >= post_date:
                        post_price_date = date
                        break
                
                if post_price_date is None:
                    print(f"No trading data available for {mention.ticker} after {post_date}")
                    continue
                
                price_at_post = stock_data.loc[stock_data.index.date == post_price_date, 'Close'].iloc[0]
                
                performance = StockPerformance(
                    ticker=mention.ticker,
                    post_date=mention.post_date,
                    price_at_post=price_at_post
                )
                
                for days, return_attr, price_attr in self.time_periods:
                    target_date = post_date + timedelta(days=days)
                    
                    closest_date = None
                    min_diff = float('inf')
                    
                    for date in available_dates:
                        if date >= target_date:
                            diff = (date - target_date).days
                            if diff < min_diff:
                                min_diff = diff
                                closest_date = date
                    
                    if closest_date and min_diff <= 5:
                        future_price = stock_data.loc[stock_data.index.date == closest_date, 'Close'].iloc[0]
                        return_pct = ((future_price - price_at_post) / price_at_post) * 100
                        
                        setattr(performance, return_attr, return_pct)
                        setattr(performance, price_attr, future_price)
                
                performances.append(performance)
                
            except Exception as e:
                print(f"Error calculating performance for {mention.ticker}: {e}")
                continue
            
            time.sleep(self.api_delay)
        
        return performances