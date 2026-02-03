#!/usr/bin/env python3
"""
MPG Mercato/Auction Performance Analyzer
Analyzes bidding patterns from MPG auction data
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class MPGMercatoAnalyzer:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        self.teams = {}
        self.team_stats = defaultdict(lambda: {
            'total_bids': 0,
            'won_auctions': 0,
            'lost_auctions': 0,
            'total_spent': 0,
            'total_lost_value': 0,
            'players_won': [],
            'players_lost': [],
            'bidding_times': []
        })

    def load_data(self):
        """Load the scraped JSON data"""
        print(f"Loading data from {self.data_file}...")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        print("✓ Data loaded successfully\n")
        return True

    def load_team_names(self):
        """Extract team names from the data"""
        # Try to get team names from teams endpoint
        teams_key = 'teams/division/mpg_division_1XQHDZXWT_23_1'

        if teams_key in self.data.get('responses', {}):
            teams_data = self.data['responses'][teams_key]

            if isinstance(teams_data, str):
                # It's base64 encoded or a string, try to parse
                try:
                    import base64
                    decoded = base64.b64decode(teams_data).decode('utf-8')
                    teams_list = json.loads(decoded)
                except:
                    teams_list = []
            elif isinstance(teams_data, list):
                teams_list = teams_data
            else:
                teams_list = []

            for team in teams_list:
                if isinstance(team, dict):
                    team_id = team.get('id')
                    team_name = team.get('name', team.get('abbreviation', team_id))
                    if team_id:
                        self.teams[team_id] = team_name

        print(f"✓ Loaded {len(self.teams)} team names\n")

    def analyze_mercato(self):
        """Analyze mercato/auction data"""
        print("="*60)
        print("ANALYZING MERCATO DATA")
        print("="*60 + "\n")

        # Get mercato data
        history_key = 'division/mpg_division_1XQHDZXWT_23_1/history'

        if history_key not in self.data.get('responses', {}):
            print("❌ No mercato history data found!")
            return False

        mercato_data = self.data['responses'][history_key].get('mercato', {})

        if not mercato_data:
            print("❌ No mercato transactions found!")
            return False

        print(f"Found {len(mercato_data)} mercato days\n")

        # Analyze each day
        total_transactions = 0

        for day, transactions in mercato_data.items():
            print(f"Day {day}: {len(transactions)} transactions")
            total_transactions += len(transactions)

            # Analyze each transaction
            for player_id, txn in transactions.items():
                player_name = f"{txn.get('firstName', '')} {txn.get('lastName', '')}".strip()
                quotation = txn.get('quotation', 0)

                # Won bid
                won_bid = txn.get('wonBid', {})
                if won_bid:
                    winner_id = won_bid.get('teamId')
                    price = won_bid.get('price', 0)
                    bid_date = won_bid.get('bidDate', '')

                    self.team_stats[winner_id]['total_bids'] += 1
                    self.team_stats[winner_id]['won_auctions'] += 1
                    self.team_stats[winner_id]['total_spent'] += price
                    self.team_stats[winner_id]['players_won'].append({
                        'name': player_name,
                        'price': price,
                        'quotation': quotation,
                        'day': day,
                        'date': bid_date,
                        'value': quotation - price  # Positive = good deal
                    })
                    self.team_stats[winner_id]['bidding_times'].append(bid_date)

                # Lost bids
                lost_bids = txn.get('lostBids', [])
                for lost_bid in lost_bids:
                    loser_id = lost_bid.get('teamId')
                    price = lost_bid.get('price', 0)
                    bid_date = lost_bid.get('bidDate', '')

                    self.team_stats[loser_id]['total_bids'] += 1
                    self.team_stats[loser_id]['lost_auctions'] += 1
                    self.team_stats[loser_id]['total_lost_value'] += price
                    self.team_stats[loser_id]['players_lost'].append({
                        'name': player_name,
                        'bid_price': price,
                        'won_price': won_bid.get('price', 0),
                        'quotation': quotation,
                        'day': day,
                        'date': bid_date
                    })
                    self.team_stats[loser_id]['bidding_times'].append(bid_date)

        print(f"\n✓ Analyzed {total_transactions} total transactions\n")
        return True

    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n" + "="*80)
        print(" "*25 + "MERCATO PERFORMANCE REPORT")
        print("="*80 + "\n")

        if not self.team_stats:
            print("⚠️  No bidding activity found\n")
            return

        # Calculate win rates and metrics
        team_metrics = []

        for team_id, stats in self.team_stats.items():
            if stats['total_bids'] == 0:
                continue

            team_name = self.teams.get(team_id, team_id[-6:])  # Use last 6 chars if no name

            win_rate = (stats['won_auctions'] / stats['total_bids'] * 100) if stats['total_bids'] > 0 else 0
            avg_price = stats['total_spent'] / stats['won_auctions'] if stats['won_auctions'] > 0 else 0

            # Calculate value efficiency (positive = good deals, negative = overpaid)
            total_value = sum(p['value'] for p in stats['players_won'])
            avg_value = total_value / stats['won_auctions'] if stats['won_auctions'] > 0 else 0

            team_metrics.append({
                'id': team_id,
                'name': team_name,
                'total_bids': stats['total_bids'],
                'won': stats['won_auctions'],
                'lost': stats['lost_auctions'],
                'win_rate': win_rate,
                'total_spent': stats['total_spent'],
                'avg_price': avg_price,
                'total_value': total_value,
                'avg_value': avg_value,
                'stats': stats
            })

        # Sort by total acquisitions (won auctions)
        team_metrics.sort(key=lambda x: x['won'], reverse=True)

        # Print overall summary
        print("📊 OVERALL SUMMARY")
        print("-" * 80)
        print(f"{'Team':<20} {'Bids':<7} {'Won':<6} {'Lost':<6} {'Win%':<8} {'Spent':<10} {'Avg€':<8} {'Value':<8}")
        print("-" * 80)

        for tm in team_metrics:
            value_symbol = "📈" if tm['avg_value'] > 0 else "📉" if tm['avg_value'] < 0 else "➖"
            print(f"{tm['name']:<20} {tm['total_bids']:<7} {tm['won']:<6} {tm['lost']:<6} "
                  f"{tm['win_rate']:<7.1f}% {tm['total_spent']:<10} {tm['avg_price']:<7.1f}€ "
                  f"{value_symbol} {tm['avg_value']:>+6.1f}")

        # Best performers
        print("\n\n🏆 BEST PERFORMERS")
        print("-" * 80)

        # Highest win rate
        by_win_rate = sorted(team_metrics, key=lambda x: x['win_rate'], reverse=True)
        print(f"\n🎯 Highest Win Rate:")
        for i, tm in enumerate(by_win_rate[:3], 1):
            print(f"   {i}. {tm['name']}: {tm['win_rate']:.1f}% ({tm['won']}/{tm['total_bids']} won)")

        # Best value (most positive value = best deals)
        by_value = sorted(team_metrics, key=lambda x: x['avg_value'], reverse=True)
        print(f"\n💰 Best Value Hunters (biggest savings vs quotation):")
        for i, tm in enumerate(by_value[:3], 1):
            print(f"   {i}. {tm['name']}: {tm['avg_value']:+.1f}€ avg value per player")

        # Most aggressive bidders
        by_total_bids = sorted(team_metrics, key=lambda x: x['total_bids'], reverse=True)
        print(f"\n🔥 Most Aggressive Bidders:")
        for i, tm in enumerate(by_total_bids[:3], 1):
            print(f"   {i}. {tm['name']}: {tm['total_bids']} total bids")

        # Biggest spenders
        by_spent = sorted(team_metrics, key=lambda x: x['total_spent'], reverse=True)
        print(f"\n💸 Biggest Spenders:")
        for i, tm in enumerate(by_spent[:3], 1):
            print(f"   {i}. {tm['name']}: {tm['total_spent']}€ spent")

        # Detailed player acquisitions
        print("\n\n📋 PLAYER ACQUISITIONS BY TEAM")
        print("-" * 80)

        for tm in team_metrics:
            if tm['won'] == 0:
                continue

            print(f"\n{tm['name']} ({tm['won']} players, {tm['total_spent']}€ spent):")

            # Sort by value (best deals first)
            players = sorted(tm['stats']['players_won'], key=lambda x: x['value'], reverse=True)

            for p in players:
                value_symbol = "✅" if p['value'] > 0 else "⚠️" if p['value'] < 0 else "➖"
                print(f"  {value_symbol} {p['name']:<25} {p['price']:>3}€ (quota: {p['quotation']}€, value: {p['value']:+}€) - Day {p['day']}")

        print("\n" + "="*80 + "\n")

    def save_analysis(self, output_file="mercato_analysis.json"):
        """Save analysis results to JSON"""
        output = {
            'analysis_timestamp': datetime.now().isoformat(),
            'source_file': str(self.data_file),
            'team_stats': {}
        }

        for team_id, stats in self.team_stats.items():
            team_name = self.teams.get(team_id, team_id)
            output['team_stats'][team_name] = {
                'total_bids': stats['total_bids'],
                'won_auctions': stats['won_auctions'],
                'lost_auctions': stats['lost_auctions'],
                'total_spent': stats['total_spent'],
                'players_won': stats['players_won'],
                'players_lost': stats['players_lost']
            }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"✓ Detailed analysis saved to: {output_file}\n")


def main():
    print("\n" + "="*80)
    print(" "*25 + "MPG MERCATO ANALYZER")
    print("="*80 + "\n")

    if len(sys.argv) < 2:
        data_file = Path("mpg_auction_data.json")
    else:
        data_file = Path(sys.argv[1])

    if not data_file.exists():
        print(f"❌ Error: File not found: {data_file}")
        return 1

    analyzer = MPGMercatoAnalyzer(data_file)

    if not analyzer.load_data():
        return 1

    analyzer.load_team_names()

    if not analyzer.analyze_mercato():
        return 1

    analyzer.generate_report()
    analyzer.save_analysis()

    print("✅ Analysis complete!\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
