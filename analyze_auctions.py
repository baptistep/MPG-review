#!/usr/bin/env python3
"""
MPG Auction Performance Analyzer

Analyzes bidding patterns and player performance from MPG auction data
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class AuctionAnalyzer:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        self.auctions = []
        self.players = {}
        self.bidders = defaultdict(lambda: {
            'total_bids': 0,
            'won_auctions': 0,
            'total_spent': 0,
            'auctions': []
        })

    def load_data(self):
        """Load the scraped JSON data"""
        print(f"Loading data from {self.data_file}...")

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print("✓ Data loaded successfully\n")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def explore_data_structure(self):
        """Explore and understand the data structure"""
        print("="*60)
        print("DATA STRUCTURE EXPLORATION")
        print("="*60)

        def print_structure(obj, indent=0, max_depth=3, current_depth=0):
            """Recursively print data structure"""
            if current_depth > max_depth:
                return

            prefix = "  " * indent

            if isinstance(obj, dict):
                for key, value in list(obj.items())[:10]:  # First 10 keys
                    if isinstance(value, (dict, list)):
                        count = len(value)
                        type_name = type(value).__name__
                        print(f"{prefix}{key}: {type_name} ({count} items)")
                        if count > 0 and current_depth < max_depth:
                            print_structure(value, indent + 1, max_depth, current_depth + 1)
                    else:
                        value_preview = str(value)[:50]
                        print(f"{prefix}{key}: {value_preview}")

            elif isinstance(obj, list) and len(obj) > 0:
                print(f"{prefix}[0]: Sample item")
                print_structure(obj[0], indent + 1, max_depth, current_depth + 1)

        print_structure(self.data)
        print()

    def find_auction_data(self):
        """Try to locate auction/trading data in the scraped JSON"""
        print("="*60)
        print("SEARCHING FOR AUCTION DATA")
        print("="*60)

        auction_keywords = ['auction', 'mercato', 'trading', 'bid', 'offer', 'transaction']

        def search_object(obj, path=""):
            """Recursively search for auction-related data"""
            found = []

            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    # Check if key contains auction keywords
                    if any(keyword in key.lower() for keyword in auction_keywords):
                        found.append((current_path, value))
                        print(f"\n✓ Found potential auction data: {current_path}")
                        print(f"  Type: {type(value).__name__}")
                        if isinstance(value, (list, dict)):
                            print(f"  Size: {len(value)} items")

                    # Recurse
                    if isinstance(value, (dict, list)):
                        found.extend(search_object(value, current_path))

            elif isinstance(obj, list):
                for i, item in enumerate(obj[:3]):  # Check first 3 items
                    current_path = f"{path}[{i}]"
                    if isinstance(item, (dict, list)):
                        found.extend(search_object(item, current_path))

            return found

        found_data = search_object(self.data)

        if found_data:
            print(f"\n✓ Found {len(found_data)} potential auction data sources")
        else:
            print("\n⚠️  No obvious auction data found")
            print("    The data might be under different keys or require API calls")

        return found_data

    def extract_api_auctions(self):
        """Extract auction data from captured API calls"""
        if 'api_calls' not in self.data:
            return []

        print("\n="*60)
        print("EXTRACTING FROM API CALLS")
        print("="*60)

        auctions = []

        for call in self.data['api_calls']:
            url = call.get('url', '')
            response = call.get('response')

            if response and isinstance(response, dict):
                # Look for auction-related endpoints
                if 'mercato' in url.lower() or 'auction' in url.lower() or 'trading' in url.lower():
                    print(f"\n✓ Found auction API: {url}")
                    print(f"  Response keys: {list(response.keys())[:10]}")
                    auctions.append({
                        'source': url,
                        'data': response
                    })

        return auctions

    def analyze_auctions(self, auction_data):
        """Analyze auction performance"""
        print("\n="*60)
        print("AUCTION ANALYSIS")
        print("="*60)

        if not auction_data:
            print("\n⚠️  No auction data available to analyze")
            return

        # This will be customized based on actual data structure
        for auction_source in auction_data:
            print(f"\nAnalyzing: {auction_source['source']}")
            data = auction_source['data']

            # Try to identify structure
            if isinstance(data, list):
                print(f"  Found {len(data)} auction items")
            elif isinstance(data, dict):
                print(f"  Found auction data with keys: {', '.join(list(data.keys())[:10])}")

    def generate_report(self):
        """Generate analysis report"""
        print("\n" + "="*60)
        print("AUCTION PERFORMANCE REPORT")
        print("="*60)

        if not self.bidders:
            print("\n⚠️  No bidder data available")
            print("\nNext steps:")
            print("1. Make sure you navigated to auction pages while running extract_data.js")
            print("2. Check that API calls were captured (look for 'api_calls' in the JSON)")
            print("3. Try running the extraction again with more interaction")
            return

        # Analyze bidders
        print("\n📊 BIDDER PERFORMANCE")
        print("-" * 60)

        bidder_stats = []
        for bidder_id, stats in self.bidders.items():
            if stats['total_bids'] > 0:
                win_rate = (stats['won_auctions'] / stats['total_bids']) * 100
                avg_spent = stats['total_spent'] / stats['won_auctions'] if stats['won_auctions'] > 0 else 0

                bidder_stats.append({
                    'id': bidder_id,
                    'total_bids': stats['total_bids'],
                    'won': stats['won_auctions'],
                    'win_rate': win_rate,
                    'total_spent': stats['total_spent'],
                    'avg_spent': avg_spent
                })

        # Sort by win rate
        bidder_stats.sort(key=lambda x: x['win_rate'], reverse=True)

        print(f"\n{'Bidder':<20} {'Bids':<8} {'Won':<8} {'Win %':<10} {'Total $':<12} {'Avg $':<10}")
        print("-" * 78)

        for stat in bidder_stats:
            print(f"{stat['id']:<20} {stat['total_bids']:<8} {stat['won']:<8} "
                  f"{stat['win_rate']:<10.1f} {stat['total_spent']:<12.0f} {stat['avg_spent']:<10.0f}")

    def save_analysis(self, output_file="auction_analysis.json"):
        """Save analysis results"""
        output = {
            'analysis_timestamp': datetime.now().isoformat(),
            'source_file': str(self.data_file),
            'bidders': dict(self.bidders),
            'auctions': self.auctions,
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Analysis saved to: {output_file}")


def main():
    print("\n" + "="*60)
    print("MPG AUCTION PERFORMANCE ANALYZER")
    print("="*60 + "\n")

    if len(sys.argv) < 2:
        print("Usage: python3 analyze_auctions.py <mpg_auction_data.json>")
        print("\nFirst, extract data using one of these methods:")
        print("  1. Browser console script (extract_data.js) - RECOMMENDED")
        print("  2. HAR file export (see SCRAPING_GUIDE.md)")
        return 1

    data_file = Path(sys.argv[1])

    if not data_file.exists():
        print(f"Error: File not found: {data_file}")
        return 1

    analyzer = AuctionAnalyzer(data_file)

    if not analyzer.load_data():
        return 1

    # Explore the data structure
    analyzer.explore_data_structure()

    # Find auction data
    found_auctions = analyzer.find_auction_data()

    # Extract from API calls
    api_auctions = analyzer.extract_api_auctions()

    # Analyze
    all_auctions = found_auctions + api_auctions
    analyzer.analyze_auctions(all_auctions)

    # Generate report
    analyzer.generate_report()

    # Save results
    analyzer.save_analysis()

    print("\n✓ Analysis complete!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
