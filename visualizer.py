"""Data visualization and analysis reporting"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

class Visualizer:
    """Creates visualizations and reports from analysis data"""
    
    def __init__(self):
        sns.set_style("whitegrid")
    
    def analyze_profitability(self, data: List[tuple]) -> Dict:
        """Analyze profitability from performance data"""
        if not data:
            return {"error": "No performance data available"}
        
        columns = ['id', 'ticker', 'post_date', 'price_at_post', 'price_1d', 'price_3d', 
                  'price_1w', 'price_2w', 'price_1m', 'return_1d', 'return_3d', 
                  'return_1w', 'return_2w', 'return_1m']
        
        df = pd.DataFrame(data, columns=columns)
        
        results = {
            'total_stocks_analyzed': len(df),
            'time_periods': {}
        }
        
        for period in ['1d', '3d', '1w', '2w', '1m']:
            return_col = f'return_{period}'
            valid_data = df[return_col].dropna()
            
            if len(valid_data) > 0:
                results['time_periods'][period] = {
                    'count': len(valid_data),
                    'mean_return': valid_data.mean(),
                    'median_return': valid_data.median(),
                    'std_return': valid_data.std(),
                    'positive_returns': (valid_data > 0).sum(),
                    'negative_returns': (valid_data < 0).sum(),
                    'win_rate': (valid_data > 0).mean() * 100,
                    'best_return': valid_data.max(),
                    'worst_return': valid_data.min(),
                    'returns_over_10pct': (valid_data > 10).sum(),
                    'returns_over_25pct': (valid_data > 25).sum(),
                    'returns_under_minus10pct': (valid_data < -10).sum(),
                }
        
        return results
    
    def print_results(self, results: Dict):
        """Print analysis results in a formatted way"""
        print("\n" + "="*60)
        print("PROFITABILITY ANALYSIS RESULTS")
        print("="*60)
        
        if 'error' in results:
            print(f"Error: {results['error']}")
            return
        
        print(f"Total stocks analyzed: {results['total_stocks_analyzed']}")
        print()
        
        for period, stats in results['time_periods'].items():
            print(f"{period.upper()} Performance:")
            print(f"  Sample size: {stats['count']}")
            print(f"  Mean return: {stats['mean_return']:.2f}%")
            print(f"  Median return: {stats['median_return']:.2f}%")
            print(f"  Win rate: {stats['win_rate']:.1f}%")
            print(f"  Best return: {stats['best_return']:.2f}%")
            print(f"  Worst return: {stats['worst_return']:.2f}%")
            print(f"  Returns > 10%: {stats['returns_over_10pct']}")
            print(f"  Returns > 25%: {stats['returns_over_25pct']}")
            print(f"  Returns < -10%: {stats['returns_under_minus10pct']}")
            print()
    
    def create_visualizations(self, data: List[tuple], output_file: str = 'reddit_pennystocks_analysis.png'):
        """Create comprehensive visualizations"""
        if not data:
            print("No data available for visualization")
            return
        
        columns = ['id', 'ticker', 'post_date', 'price_at_post', 'price_1d', 'price_3d', 
                  'price_1w', 'price_2w', 'price_1m', 'return_1d', 'return_3d', 
                  'return_1w', 'return_2w', 'return_1m']
        
        df = pd.DataFrame(data, columns=columns)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Reddit r/pennystocks Performance Analysis', fontsize=16)
        
        periods = ['1d', '3d', '1w', '2w', '1m']
        
        # Distribution plots
        for i, period in enumerate(periods):
            row = i // 3
            col = i % 3
            
            return_col = f'return_{period}'
            valid_data = df[return_col].dropna()
            
            if len(valid_data) > 0:
                axes[row, col].hist(valid_data, bins=30, alpha=0.7, edgecolor='black')
                axes[row, col].axvline(valid_data.mean(), color='red', linestyle='--', 
                                     label=f'Mean: {valid_data.mean():.1f}%')
                axes[row, col].axvline(0, color='black', linestyle='-', alpha=0.5)
                axes[row, col].set_title(f'{period.upper()} Returns Distribution')
                axes[row, col].set_xlabel('Return (%)')
                axes[row, col].set_ylabel('Frequency')
                axes[row, col].legend()
        
        # Summary statistics plot
        summary_data = []
        for period in periods:
            return_col = f'return_{period}'
            valid_data = df[return_col].dropna()
            if len(valid_data) > 0:
                summary_data.append({
                    'Period': period.upper(),
                    'Mean Return (%)': valid_data.mean(),
                    'Win Rate (%)': (valid_data > 0).mean() * 100
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            ax = axes[1, 2]
            
            x = range(len(summary_df))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], summary_df['Mean Return (%)'], 
                  width, label='Mean Return (%)', alpha=0.7)
            ax2 = ax.twinx()
            ax2.bar([i + width/2 for i in x], summary_df['Win Rate (%)'], 
                   width, label='Win Rate (%)', alpha=0.7, color='orange')
            
            ax.set_xlabel('Time Period')
            ax.set_ylabel('Mean Return (%)')
            ax2.set_ylabel('Win Rate (%)')
            ax.set_title('Summary Statistics')
            ax.set_xticks(x)
            ax.set_xticklabels(summary_df['Period'])
            ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
        plt.show()