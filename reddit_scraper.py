import praw
from datetime import datetime
from typing import List
from models import StockMention
from ticker_extractor import TickerExtractor

class RedditScraper:
    """Scrapes Reddit for stock mentions"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str, subreddit: str, validation_delay: float = 0.2):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.subreddit_name = subreddit
        # allow speeding up validation during tests by passing validation_delay
        self.ticker_extractor = TickerExtractor(validation_delay=validation_delay)
    
    def fetch_posts(
        self,
        limit: int = 100,
        use_title_only: bool = True,
        sort_by: str = "top",
        time_filter: str = "month"
    ) -> List[StockMention]:
        """
        Fetch posts from subreddit and extract stock mentions

        Args:
            limit: Number of posts to fetch
            use_title_only: If True, only analyze post titles (primitive mode)
            sort_by: 'hot', 'new', 'top', 'rising'
            time_filter: applies only when sort_by == 'top' ('day','week','month','year','all')
            
        Returns:
            List of StockMention objects
        """
        subreddit = self.reddit.subreddit(self.subreddit_name)
        mentions = []

        print(f"Fetching {limit} posts from r/{self.subreddit_name} "
              f"(sort_by={sort_by}, time_filter={time_filter}, title_only={use_title_only})...")

        # choose generator based on sort_by
        if sort_by == "hot":
            posts = subreddit.hot(limit=limit)
        elif sort_by == "new":
            posts = subreddit.new(limit=limit)
        elif sort_by == "rising":
            posts = subreddit.rising(limit=limit)
        elif sort_by == "top":
            posts = subreddit.top(limit=limit, time_filter=time_filter)
        else:
            raise ValueError(f"Invalid sort option: {sort_by}")

        for post in posts:
            text_to_analyze = post.title if use_title_only else f"{post.title} {post.selftext}"
            tickers = self.ticker_extractor.extract_tickers_from_text(text_to_analyze)

            # skip posts with no tickers
            if not tickers:
                continue

            post_date = datetime.fromtimestamp(post.created_utc)

            for ticker in tickers:
                mention = StockMention(
                    ticker=ticker,
                    post_id=post.id,
                    post_title=post.title,
                    post_date=post_date,
                    post_score=post.score,
                    post_url=f"https://reddit.com{post.permalink}",
                    author=str(post.author) if post.author else "deleted"
                )
                mentions.append(mention)

        print(f"Found {len(mentions)} stock mentions in {len(set([m.post_id for m in mentions]))} posts")
        return mentions