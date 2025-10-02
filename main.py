"""Main entry point for Reddit stocks profitability analyzer"""

from config import Config
from reddit_scraper import RedditScraper
from stock_analyzer import StockAnalyzer
from database import Database
from visualizer import Visualizer

class RedditStockAnalyzerApp:
    """Main application orchestrator"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database(self.config.DATABASE_NAME)
        self.scraper = RedditScraper(
            client_id=self.config.REDDIT_CLIENT_ID,
            client_secret=self.config.REDDIT_CLIENT_SECRET,
            user_agent=self.config.REDDIT_USER_AGENT,
            subreddit=self.config.SUBREDDIT_NAME
        )
        self.analyzer = StockAnalyzer()
        self.visualizer = Visualizer()
    
    def run_analysis(self, num_posts: int = None, title_only: bool = True, sort_by: str = 'top', time_filter: str = 'month'):
        """Run the complete analysis pipeline
        
        Args:
            num_posts: Number of posts to analyze
            title_only: If True, only analyze post titles (recommended for accuracy)
            sort_by: How to sort posts - 'hot', 'new', 'top', 'rising'
            time_filter: Time filter for 'top' sorting - 'day', 'week', 'month', 'year', 'all'
        """
        if num_posts is None:
            num_posts = self.config.DEFAULT_POST_LIMIT
        
        print("Starting Reddit r/pennystocks profitability analysis...")
        
        # Step 1: Fetch Reddit posts
        mentions = self.scraper.fetch_posts(
            limit=num_posts,
            use_title_only=title_only,
            sort_by=sort_by,
            time_filter=time_filter
        )
        
        if not mentions:
            print("No stock mentions found!")
            return
        
        # Step 2: Calculate performance
        performances = self.analyzer.calculate_performance(mentions)
        
        if not performances:
            print("No valid performance data calculated!")
            return
        
        # Step 3: Save to database
        self.db.save_mentions(mentions)
        self.db.save_performances(performances)
        
        # Step 3.5: Run diagnostics
        self.db.diagnose_database()
        
        # Step 4: Analyze profitability
        data = self.db.get_all_performance_data()
        results = self.visualizer.analyze_profitability(data)
        
        # Step 5: Print results
        self.visualizer.print_results(results)
        
        # Step 6: Create visualizations
        self.visualizer.create_visualizations(data)
        
        return results
    
    def cleanup(self):
        """Cleanup resources"""
        self.db.close()

def main():
    """Main entry point"""
    app = RedditStockAnalyzerApp()
    
    try:
        # Run analysis with different options:
        
        # Option 1: Get top posts from the past MONTH (recommended for older posts)
        results = app.run_analysis(num_posts=50, title_only=True, sort_by='top', time_filter='month')
        
        # Option 2: Get top posts from the past WEEK
        # results = app.run_analysis(num_posts=50, title_only=True, sort_by='top', time_filter='week')
        
        # Option 3: Get newest posts (may be too recent for analysis)
        # results = app.run_analysis(num_posts=50, title_only=True, sort_by='new')
        
        # Option 4: Get hot posts (current default, often recent)
        # results = app.run_analysis(num_posts=50, title_only=True, sort_by='hot')
        
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()