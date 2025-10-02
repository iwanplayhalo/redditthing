"""Data models for the Reddit stocks analyzer"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StockMention:
    """Data class to store stock mention information"""
    ticker: str
    post_id: str
    post_title: str
    post_date: datetime
    post_score: int
    post_url: str
    author: str

@dataclass
class StockPerformance:
    """Data class to store stock performance data"""
    ticker: str
    post_date: datetime
    price_at_post: float
    price_1d: Optional[float] = None
    price_3d: Optional[float] = None
    price_1w: Optional[float] = None
    price_2w: Optional[float] = None
    price_1m: Optional[float] = None
    return_1d: Optional[float] = None
    return_3d: Optional[float] = None
    return_1w: Optional[float] = None
    return_2w: Optional[float] = None
    return_1m: Optional[float] = None