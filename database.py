"""Database operations for storing and retrieving stock data"""

import sqlite3
from typing import List, Dict
from models import StockMention, StockPerformance

class Database:
    """Handles all database operations"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database and create tables"""
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_mentions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                post_id TEXT,
                post_title TEXT,
                post_date TEXT,
                post_score INTEGER,
                post_url TEXT,
                author TEXT,
                UNIQUE(ticker, post_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                post_date TEXT,
                price_at_post REAL,
                price_1d REAL,
                price_3d REAL,
                price_1w REAL,
                price_2w REAL,
                price_1m REAL,
                return_1d REAL,
                return_3d REAL,
                return_1w REAL,
                return_2w REAL,
                return_1m REAL,
                UNIQUE(ticker, post_date)
            )
        ''')
        
        self.conn.commit()
    
    def save_mentions(self, mentions: List[StockMention]):
        """Save stock mentions to database"""
        cursor = self.conn.cursor()
        
        for mention in mentions:
            cursor.execute('''
                INSERT OR REPLACE INTO stock_mentions 
                (ticker, post_id, post_title, post_date, post_score, post_url, author)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                mention.ticker, mention.post_id, mention.post_title,
                mention.post_date.isoformat(), mention.post_score,
                mention.post_url, mention.author
            ))
        
        self.conn.commit()
        print(f"Saved {len(mentions)} mentions to database")
    
    def save_performances(self, performances: List[StockPerformance]):
        """Save stock performance data to database"""
        cursor = self.conn.cursor()
        
        saved_count = 0
        for perf in performances:
            cursor.execute('''
                INSERT OR REPLACE INTO stock_performance
                (ticker, post_date, price_at_post, price_1d, price_3d, price_1w, price_2w, price_1m,
                 return_1d, return_3d, return_1w, return_2w, return_1m)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                perf.ticker, perf.post_date.isoformat(), perf.price_at_post,
                perf.price_1d, perf.price_3d, perf.price_1w, perf.price_2w, perf.price_1m,
                perf.return_1d, perf.return_3d, perf.return_1w, perf.return_2w, perf.return_1m
            ))
            saved_count += 1
            
            # Debug output
            returns = []
            if perf.return_1d is not None:
                returns.append(f"1d:{perf.return_1d:.1f}%")
            if perf.return_3d is not None:
                returns.append(f"3d:{perf.return_3d:.1f}%")
            if perf.return_1w is not None:
                returns.append(f"1w:{perf.return_1w:.1f}%")
            if perf.return_2w is not None:
                returns.append(f"2w:{perf.return_2w:.1f}%")
            if perf.return_1m is not None:
                returns.append(f"1m:{perf.return_1m:.1f}%")
            
            print(f"  Saved {perf.ticker}: [{', '.join(returns)}]")
        
        self.conn.commit()
        print(f"\n✓ Saved {saved_count} performance records to database")
    
    def get_all_performance_data(self) -> List[tuple]:
        """Retrieve all performance data from database (with ANY return data)"""
        cursor = self.conn.cursor()
        # Get records with ANY return data, not just 1d
        cursor.execute('''
            SELECT * FROM stock_performance 
            WHERE return_1d IS NOT NULL 
               OR return_3d IS NOT NULL 
               OR return_1w IS NOT NULL 
               OR return_2w IS NOT NULL 
               OR return_1m IS NOT NULL
        ''')
        return cursor.fetchall()
    
    def diagnose_database(self):
        """Diagnose what's in the database"""
        cursor = self.conn.cursor()
        
        print("\n" + "="*60)
        print("DATABASE DIAGNOSTICS")
        print("="*60)
        
        # Check mentions
        cursor.execute('SELECT COUNT(*) FROM stock_mentions')
        mention_count = cursor.fetchone()[0]
        print(f"\n📊 Stock Mentions: {mention_count}")
        
        if mention_count > 0:
            cursor.execute('SELECT ticker, COUNT(*) as count FROM stock_mentions GROUP BY ticker ORDER BY count DESC LIMIT 10')
            print("\nTop mentioned tickers:")
            for ticker, count in cursor.fetchall():
                print(f"  {ticker}: {count} mentions")
        
        # Check all performance records
        cursor.execute('SELECT COUNT(*) FROM stock_performance')
        perf_count = cursor.fetchone()[0]
        print(f"\n📈 Performance Records: {perf_count}")
        
        if perf_count > 0:
            cursor.execute('''
                SELECT ticker, 
                       COUNT(*) as total,
                       SUM(CASE WHEN return_1d IS NOT NULL THEN 1 ELSE 0 END) as has_1d,
                       SUM(CASE WHEN return_3d IS NOT NULL THEN 1 ELSE 0 END) as has_3d,
                       SUM(CASE WHEN return_1w IS NOT NULL THEN 1 ELSE 0 END) as has_1w,
                       SUM(CASE WHEN return_2w IS NOT NULL THEN 1 ELSE 0 END) as has_2w,
                       SUM(CASE WHEN return_1m IS NOT NULL THEN 1 ELSE 0 END) as has_1m
                FROM stock_performance 
                GROUP BY ticker
            ''')
            
            print("\nPerformance data by ticker:")
            print("Ticker | Records | 1d | 3d | 1w | 2w | 1m")
            print("-" * 50)
            for row in cursor.fetchall():
                ticker, total, d1, d3, w1, w2, m1 = row
                print(f"{ticker:6} | {total:7} | {d1:2} | {d3:2} | {w1:2} | {w2:2} | {m1:2}")
        
        # Check records with ANY return data
        cursor.execute('''
            SELECT COUNT(*) FROM stock_performance 
            WHERE return_1d IS NOT NULL 
               OR return_3d IS NOT NULL 
               OR return_1w IS NOT NULL 
               OR return_2w IS NOT NULL 
               OR return_1m IS NOT NULL
        ''')
        records_with_data = cursor.fetchone()[0]
        print(f"\n✓ Records with ANY return data: {records_with_data}")
        
        # Show sample of actual data
        cursor.execute('''
            SELECT ticker, post_date, price_at_post, return_1d, return_3d, return_1w, return_2w, return_1m
            FROM stock_performance
            LIMIT 5
        ''')
        
        print("\nSample performance records:")
        print("Ticker | Date | Price | 1d | 3d | 1w | 2w | 1m")
        print("-" * 80)
        for row in cursor.fetchall():
            ticker, date, price, r1d, r3d, r1w, r2w, r1m = row
            date_str = date[:10] if date else "N/A"
            price_str = f"${price:.2f}" if price else "N/A"
            r1d_str = f"{r1d:+.1f}%" if r1d else "None"
            r3d_str = f"{r3d:+.1f}%" if r3d else "None"
            r1w_str = f"{r1w:+.1f}%" if r1w else "None"
            r2w_str = f"{r2w:+.1f}%" if r2w else "None"
            r1m_str = f"{r1m:+.1f}%" if r1m else "None"
            print(f"{ticker:6} | {date_str} | {price_str:8} | {r1d_str:7} | {r3d_str:7} | {r1w_str:7} | {r2w_str:7} | {r1m_str:7}")
        
        print("="*60 + "\n")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()