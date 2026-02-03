#!/usr/bin/env python3
"""
MPG Fun Auction Report Generator
Creates an entertaining HTML report with roasts, stats, and visualizations
"""

import json
from pathlib import Path
from collections import defaultdict
import base64


class FunReportGenerator:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = None
        self.teams = {}
        self.players = {}
        self.clubs = {}
        self.team_stats = defaultdict(lambda: {
            'total_bids': 0,
            'won_auctions': 0,
            'total_spent': 0,
            'players_won': [],
            'total_goals': 0,
            'total_avg_rating': 0,
            'total_avg_points': 0,
            'clubs_represented': set(),
            'positions': defaultdict(int)
        })

        # Ligue 1 club mappings (verified from user input)
        self.club_names = {
            'mpg_championship_club_138': 'AJ Auxerre',  # Sinayoko, Faivre
            'mpg_championship_club_141': 'Le Havre',  # Boufal, Soumaré
            'mpg_championship_club_142': 'Lens',  # Thauvin, Gorgelin, Thomasson
            'mpg_championship_club_143': 'Lyon',  # Tolisso, Fofana, Endrick, Clinton Mata
            'mpg_championship_club_144': 'Marseille',  # Greenwood, Aubameyang, Rulli
            'mpg_championship_club_145': 'Rennes',  # Habib Diallo
            'mpg_championship_club_146': 'Monaco',  # Akliouche, Minamino, Balogun, Golovin
            'mpg_championship_club_147': 'Nice',
            'mpg_championship_club_148': 'Nantes',
            'mpg_championship_club_149': 'PSG',  # Zaïre-Emery, Barcola, Dembélé, Lee Kang-In
            'mpg_championship_club_150': 'Rennes',  # Frankowski, Brice Samba, Rongier
            'mpg_championship_club_151': 'Brest',
            'mpg_championship_club_152': 'Reims',
            'mpg_championship_club_153': 'Strasbourg',  # Julio Enciso, Emegha
            'mpg_championship_club_154': 'Toulouse',
            'mpg_championship_club_155': 'Saint-Étienne',
            'mpg_championship_club_156': 'Angers',
            'mpg_championship_club_157': 'Montpellier',
            'mpg_championship_club_427': 'Caen',
            'mpg_championship_club_429': 'Lille',  # Giroud, Benjamin André, Haraldsson
            'mpg_championship_club_430': 'Dortmund',
            'mpg_championship_club_694': 'PSV',
            'mpg_championship_club_862': 'Brest',
            'mpg_championship_club_1395': 'Lens',
            'mpg_championship_club_2128': 'Clermont',
            'mpg_championship_club_2338': 'Bournemouth',
        }

    def load_data(self):
        """Load all data"""
        print("Loading data...")
        with open(self.data_file, 'r') as f:
            self.data = json.load(f)

        # Load players with stats
        players_key = 'championship-players-pool/1/details'
        if players_key in self.data['responses']:
            for player in self.data['responses'][players_key]['players']:
                player_id = player['id']
                self.players[player_id] = player

        # Load teams
        teams_key = 'teams/division/mpg_division_1XQHDZXWT_23_1'
        if teams_key in self.data.get('responses', {}):
            teams_data = self.data['responses'][teams_key]
            if isinstance(teams_data, str):
                try:
                    decoded = base64.b64decode(teams_data).decode('utf-8')
                    teams_list = json.loads(decoded)
                    for team in teams_list:
                        self.teams[team['id']] = team
                except:
                    pass

        print(f"✓ Loaded {len(self.players)} players")
        print(f"✓ Loaded {len(self.teams)} teams\n")

    def analyze_auctions(self):
        """Analyze auctions with player stats"""
        print("Analyzing auctions...")

        mercato = self.data['responses']['division/mpg_division_1XQHDZXWT_23_1/history']['mercato']

        # Track most contested players
        self.contested_players = []

        for day, transactions in mercato.items():
            for player_id, txn in transactions.items():
                won_bid = txn.get('wonBid', {})
                if not won_bid:
                    continue

                team_id = won_bid['teamId']
                price = won_bid['price']

                # Get player stats
                player_stats = self.players.get(player_id, {})
                stats = player_stats.get('stats', {})

                # Get club name from mapping
                club_id = txn.get('clubId', '')
                club_name = self.club_names.get(club_id, club_id.replace('mpg_championship_club_', 'Club #') if club_id else 'Unknown')

                # Count total bidders for this player
                lost_bids = txn.get('lostBids', [])
                total_bidders = 1 + len(lost_bids)  # Winner + losers

                player_info = {
                    'id': player_id,
                    'name': f"{txn.get('firstName', '')} {txn.get('lastName', '')}".strip(),
                    'price': price,
                    'quotation': txn.get('quotation', 0),
                    'value': txn.get('quotation', 0) - price,
                    'position': txn.get('position', 0),
                    'clubId': club_id,
                    'club': club_name,
                    'day': day,
                    'total_bidders': total_bidders,
                    # Stats
                    'avgRating': stats.get('averageRating', 0),
                    'avgPoints': stats.get('averagePoints', 0),
                    'totalGoals': stats.get('totalGoals', 0),
                    'totalMatches': stats.get('totalPlayedMatches', 0),
                    'totalCleanSheets': stats.get('totalCleanSheets', 0),
                    'totalYellowCards': stats.get('totalYellowCards', 0),
                    'totalRedCards': stats.get('totalRedCards', 0),
                }

                # Track contested players (3+ bidders)
                if total_bidders >= 3:
                    self.contested_players.append({
                        'player': player_info,
                        'winner': self.teams.get(team_id, {}).get('name', team_id[-6:]),
                        'winner_id': team_id,
                        'total_bidders': total_bidders,
                        'lost_bids': lost_bids
                    })

                self.team_stats[team_id]['total_bids'] += 1
                self.team_stats[team_id]['won_auctions'] += 1
                self.team_stats[team_id]['total_spent'] += price
                self.team_stats[team_id]['players_won'].append(player_info)
                self.team_stats[team_id]['total_goals'] += player_info['totalGoals']
                self.team_stats[team_id]['total_avg_rating'] += player_info['avgRating']
                self.team_stats[team_id]['total_avg_points'] += player_info['avgPoints']
                # Track club diversity (use club name, not empty strings)
                if club_name and club_name != 'Unknown':
                    self.team_stats[team_id]['clubs_represented'].add(club_name)
                self.team_stats[team_id]['positions'][player_info['position']] += 1

        print("✓ Analysis complete\n")

    def calculate_team_scores(self):
        """Calculate team quality scores"""
        team_scores = []

        for team_id, stats in self.team_stats.items():
            team_name = self.teams.get(team_id, {}).get('name', team_id[-6:])

            num_players = stats['won_auctions']
            if num_players == 0:
                continue

            avg_rating = stats['total_avg_rating'] / num_players
            avg_points = stats['total_avg_points'] / num_players
            total_goals = stats['total_goals']

            # Calculate win rate
            win_rate = (stats['won_auctions'] / stats['total_bids'] * 100) if stats['total_bids'] > 0 else 0

            # Calculate "quality score" (weighted)
            quality_score = (
                avg_rating * 10 +  # Rating weight
                avg_points * 5 +   # Points weight
                total_goals * 2    # Goals weight
            )

            # Value efficiency (lower is better)
            total_value_lost = sum(p['value'] for p in stats['players_won'])
            value_efficiency = total_value_lost / num_players if num_players > 0 else 0

            team_scores.append({
                'id': team_id,
                'name': team_name,
                'quality_score': quality_score,
                'avg_rating': avg_rating,
                'avg_points': avg_points,
                'total_goals': total_goals,
                'num_players': num_players,
                'value_efficiency': value_efficiency,
                'clubs_diversity': len(stats['clubs_represented']),
                'win_rate': win_rate,
                'stats': stats
            })

        return sorted(team_scores, key=lambda x: x['quality_score'], reverse=True)

    def calculate_silly_awards(self, team_scores):
        """Calculate fun awards for teams"""
        awards = {}

        all_players = []
        for team in team_scores:
            all_players.extend([(team['name'], p) for p in team['stats']['players_won']])

        # Money Bags Award - Most expensive single player
        most_expensive = max(all_players, key=lambda x: x[1]['price'])
        awards['money_bags'] = {
            'winner': most_expensive[0],
            'description': f"Paid **{most_expensive[1]['price']}€** for **{most_expensive[1]['name']}** ({most_expensive[1]['club']})",
            'emoji': '💰',
            'title': 'Money Bags Award'
        }

        # Charity Case Award - Biggest overpay
        biggest_overpay = min(all_players, key=lambda x: x[1]['value'])
        awards['charity'] = {
            'winner': biggest_overpay[0],
            'description': f"Overpaid **{abs(biggest_overpay[1]['value'])}€** for **{biggest_overpay[1]['name']}** ({biggest_overpay[1]['club']})",
            'emoji': '🎁',
            'title': 'Charity Case Award'
        }

        # Bargain Hunter Award - Best value find (among players costing >10€)
        expensive_players = [p for p in all_players if p[1]['price'] >= 10]
        if expensive_players:
            best_value = max(expensive_players, key=lambda x: x[1]['value'])
            if best_value[1]['value'] >= 0:
                awards['bargain'] = {
                    'winner': best_value[0],
                    'description': f"**{best_value[1]['name']}** ({best_value[1]['club']}) for {best_value[1]['price']}€ (quota: {best_value[1]['quotation']}€) - Actually good value!",
                    'emoji': '🛒',
                    'title': 'Bargain Hunter Award'
                }

        # Goal Machine Award
        goal_king = max(team_scores, key=lambda x: x['total_goals'])
        awards['goal_machine'] = {
            'winner': goal_king['name'],
            'description': f"**{goal_king['total_goals']} total goals** across the squad!",
            'emoji': '⚽',
            'title': 'Goal Machine Award'
        }

        # Defensive Masterclass Award - Most GKs + Defenders
        def count_defensive(team):
            positions = team['stats']['positions']
            return positions.get(1, 0) + positions.get(2, 0)

        defensive_king = max(team_scores, key=count_defensive)
        awards['defensive'] = {
            'winner': defensive_king['name'],
            'description': f"**{count_defensive(defensive_king)} goalkeepers & defenders**. Clean sheets incoming!",
            'emoji': '🛡️',
            'title': 'Defensive Masterclass'
        }

        # World Traveler Award - Most diverse clubs
        most_diverse = max(team_scores, key=lambda x: x['clubs_diversity'])
        awards['traveler'] = {
            'winner': most_diverse['name'],
            'description': f"**{most_diverse['clubs_diversity']} different clubs**. Passport fully stamped!",
            'emoji': '🌍',
            'title': 'World Traveler Award'
        }

        # Local Hero Award - Most players from one club
        local_hero_team = None
        max_from_one_club = 0
        fav_club_name = ""

        for team in team_scores:
            club_counts = {}
            for p in team['stats']['players_won']:
                club = p['club']
                if club and club != 'Unknown':
                    club_counts[club] = club_counts.get(club, 0) + 1

            if club_counts:
                top_club, count = max(club_counts.items(), key=lambda x: x[1])
                if count > max_from_one_club:
                    max_from_one_club = count
                    local_hero_team = team['name']
                    fav_club_name = top_club

        if local_hero_team:
            awards['local_hero'] = {
                'winner': local_hero_team,
                'description': f"**{max_from_one_club} players from {fav_club_name}**. Season ticket holder?",
                'emoji': '🏟️',
                'title': 'Local Hero Award'
            }

        # The Gambler Award - Lowest win rate among active bidders
        active_bidders = [t for t in team_scores if t['stats']['total_bids'] >= 20]
        if active_bidders:
            gambler = min(active_bidders, key=lambda x: x['win_rate'])
            awards['gambler'] = {
                'winner': gambler['name'],
                'description': f"Only **{gambler['win_rate']:.1f}% win rate** with {gambler['stats']['total_bids']} bids. Keep trying!",
                'emoji': '🎲',
                'title': 'The Gambler Award'
            }

        # Sniper Award - Highest win rate
        sniper = max(team_scores, key=lambda x: x['win_rate'])
        awards['sniper'] = {
            'winner': sniper['name'],
            'description': f"**{sniper['win_rate']:.1f}% win rate**. Clinical precision!",
            'emoji': '🎯',
            'title': 'Sniper Award'
        }

        # The Benchwarmer Award - Lowest total matches played
        total_matches_played = {team['name']: sum(p['totalMatches'] for p in team['stats']['players_won'])
                               for team in team_scores}
        benchwarmer = min(total_matches_played.items(), key=lambda x: x[1])
        awards['benchwarmer'] = {
            'winner': benchwarmer[0],
            'description': f"Squad has only **{benchwarmer[1]} total matches played**. Hope they're not injured!",
            'emoji': '🪑',
            'title': 'Benchwarmer Brigade'
        }

        # The Yellow Card Collector
        total_yellows = {team['name']: sum(p['totalYellowCards'] for p in team['stats']['players_won'])
                        for team in team_scores}
        card_collector = max(total_yellows.items(), key=lambda x: x[1])
        if card_collector[1] > 0:
            awards['yellow_cards'] = {
                'winner': card_collector[0],
                'description': f"**{card_collector[1]} yellow cards** in the squad. Aggressive much?",
                'emoji': '🟨',
                'title': 'Card Collector Award'
            }

        return awards

    def generate_psychological_profiles(self, team_scores):
        """Generate psychological profiles based on bidding behavior"""
        profiles = {}

        for team in team_scores:
            name = team['name']
            stats = team['stats']

            if stats['won_auctions'] == 0:
                continue

            profile = {
                'archetype': '',
                'traits': [],
                'description': '',
                'strategy': '',
                'emotional_state': ''
            }

            # Analyze bidding behavior
            win_rate = team['win_rate']
            avg_overpay = abs(team['value_efficiency'])
            total_bids = stats['total_bids']

            # Position preferences
            positions = stats['positions']
            total_players = sum(positions.values())
            fwd_pct = (positions.get(4, 0) / total_players * 100) if total_players > 0 else 0
            def_pct = ((positions.get(1, 0) + positions.get(2, 0)) / total_players * 100) if total_players > 0 else 0

            # Goals analysis
            total_goals = team['total_goals']

            # Club diversity
            club_diversity = team['clubs_diversity']

            # Determine archetype based on behavior
            if win_rate > 90:
                profile['archetype'] = "🎯 The Sniper"
                profile['traits'].append("Extremely selective")
                profile['traits'].append("Waits for the perfect moment")
                profile['strategy'] = "Only bids when victory is certain. Probably has a spreadsheet with player values."
            elif win_rate > 75:
                profile['archetype'] = "🧠 The Strategist"
                profile['traits'].append("Calculated risk-taker")
                profile['traits'].append("High success rate")
                profile['strategy'] = "Picks targets carefully and executes with precision. Knows when to walk away."
            elif win_rate > 60:
                profile['archetype'] = "⚖️ The Balanced Player"
                profile['traits'].append("Mix of wins and losses")
                profile['traits'].append("Moderate approach")
                profile['strategy'] = "Takes measured risks. Not afraid to compete but knows their limits."
            elif win_rate < 50:
                profile['archetype'] = "🎲 The Gambler"
                profile['traits'].append("Shoots at everything")
                profile['traits'].append("High risk tolerance")
                profile['strategy'] = "If you don't try, you don't win! Throws bids everywhere hoping something sticks."
            else:
                profile['archetype'] = "🏃 The Competitor"
                profile['traits'].append("Enjoys the battle")
                profile['traits'].append("Wins some, loses some")
                profile['strategy'] = "Competitive spirit. Doesn't mind losing if the fight was good."

            # Money behavior
            if avg_overpay > 15:
                profile['traits'].append("Deep pockets syndrome")
                profile['emotional_state'] = "💸 Money is no object! Will pay whatever it takes to win."
            elif avg_overpay > 10:
                profile['traits'].append("Premium buyer")
                profile['emotional_state'] = "💰 Willing to pay extra for quality. Budget? What budget?"
            elif avg_overpay > 5:
                profile['traits'].append("Fair market buyer")
                profile['emotional_state'] = "📊 Pays market rates. Reasonable and balanced approach."
            else:
                profile['traits'].append("Value hunter")
                profile['emotional_state'] = "🛒 Bargain hunter! Every euro counts."

            # Position strategy
            if fwd_pct > 40:
                profile['traits'].append("Attack-minded")
                profile['description'] = f"**Attack is the best defense!** Loaded up on forwards ({positions.get(4, 0)} strikers). Believes in outscoring opponents rather than keeping clean sheets."
            elif def_pct > 50:
                profile['traits'].append("Defensive mastermind")
                profile['description'] = f"**Defense wins championships!** Stacked the backline with {positions.get(2, 0)} defenders. Probably dreams about 1-0 victories."
            else:
                profile['description'] = f"**Balanced squad builder.** {positions.get(4, 0)} forwards, {positions.get(3, 0)} midfielders, {positions.get(2, 0)} defenders. Textbook approach."

            # Goal scoring psychology
            if total_goals > 35:
                profile['traits'].append("Goal machine collector")
                profile['description'] += f" Assembled a squad with **{total_goals} goals**. Loves the beautiful game when it ends 5-4!"
            elif total_goals < 15:
                profile['traits'].append("Potential over performance")
                profile['description'] += f" Only {total_goals} goals in the squad though... Hope they perform better than their stats suggest!"

            # Club loyalty analysis
            club_counts = {}
            for p in stats['players_won']:
                club = p['club']
                if club and club != 'Unknown':
                    club_counts[club] = club_counts.get(club, 0) + 1

            if club_counts:
                fav_club = max(club_counts.items(), key=lambda x: x[1])
                if fav_club[1] >= 4:
                    profile['traits'].append(f"{fav_club[0]} super fan")
                    profile['description'] += f" Has a **{fav_club[0]} obsession** ({fav_club[1]} players). Season ticket holder confirmed!"

            if club_diversity >= 18:
                profile['traits'].append("Globe trotter")
                profile['description'] += f" Raided **{club_diversity} different clubs**. Treats Ligue 1 like a shopping mall!"
            elif club_diversity <= 10:
                profile['traits'].append("Local loyalist")
                profile['description'] += f" Only shopped at {club_diversity} clubs. Believes in keeping it simple."

            # Bidding aggression analysis
            contested_won = sum(1 for c in self.contested_players if c['winner_id'] == team['id'])
            if contested_won >= 5:
                profile['traits'].append("Loves the battle")
                profile['emotional_state'] += f" Won **{contested_won} contested auctions**. Thrives in bidding wars!"
            elif total_bids >= 35:
                profile['traits'].append("Trigger happy")
                profile['emotional_state'] += f" Placed **{total_bids} bids**! Can't resist clicking that bid button."
            elif total_bids <= 25:
                profile['traits'].append("Patient observer")
                profile['emotional_state'] += f" Only {total_bids} bids. Watches others fight, then swoops in."

            # Overall personality assessment
            if avg_overpay > 12 and fwd_pct > 35:
                profile['personality'] = "🌟 **The Showboat** - Wants the flashy attackers and will pay anything for them. Football is entertainment!"
            elif win_rate > 75 and avg_overpay < 8:
                profile['personality'] = "🎓 **The Professor** - Calculated, smart, and efficient. Probably studied economics."
            elif total_bids > 40 and win_rate < 55:
                profile['personality'] = "🎪 **The Chaos Agent** - Bids on everything, wins some, loses more. But what a ride!"
            elif def_pct > 45 and avg_overpay < 10:
                profile['personality'] = "🛡️ **The Fortress Builder** - Pragmatic and defensive. Wins 1-0 and sleeps well."
            elif contested_won >= 4:
                profile['personality'] = "⚔️ **The Warrior** - Lives for the fight. Contested auctions are their playground."
            else:
                profile['personality'] = "🎯 **The Pragmatist** - Does what works. No flashy moves, just solid decisions."

            profiles[name] = profile

        return profiles

    def generate_roasts(self, team_scores):
        """Generate fun roasts and commentary"""
        roasts = {}

        for i, team in enumerate(team_scores, 1):
            name = team['name']
            stats = team['stats']

            roast = []

            # Position-based roasts
            if i == 1:
                roast.append("🏆 **THE CHAMPION** - Somehow assembled a squad that doesn't look like a relegation battle!")
            elif i == len(team_scores):
                roast.append("🤡 **WOODEN SPOON ALERT** - Did you bid with your eyes closed?")

            # Value efficiency roasts
            if team['value_efficiency'] < -15:
                roast.append(f"💸 You paid an average of **{abs(team['value_efficiency']):.1f}€ OVER quotation**. That's not bidding, that's charity!")
            elif team['value_efficiency'] < -10:
                roast.append(f"💰 Overpaid by {abs(team['value_efficiency']):.1f}€ per player. Someone's got deep pockets!")

            # Goals roasts
            if team['total_goals'] < 5:
                roast.append(f"⚽ Only **{team['total_goals']} goals** combined? Hope you enjoy 0-0 draws!")
            elif team['total_goals'] > 30:
                roast.append(f"🔥 **{team['total_goals']} goals!** Did you buy the entire attacking line?")

            # Diversity roasts
            if team['clubs_diversity'] < 10:
                roast.append(f"🏟️ Only {team['clubs_diversity']} different clubs? Local bias much?")
            elif team['clubs_diversity'] > 18:
                roast.append(f"🌍 {team['clubs_diversity']} different clubs - are you collecting Panini stickers?")

            # Rating roasts
            if team['avg_rating'] < 4.5:
                roast.append(f"📉 Average rating: {team['avg_rating']:.2f}. That's... not good, mate.")
            elif team['avg_rating'] > 5.5:
                roast.append(f"⭐ Average rating: {team['avg_rating']:.2f}. Actually impressive!")

            # Specific player roasts
            players = stats['players_won']

            # Find biggest overpay
            worst_value = min(players, key=lambda x: x['value'])
            if worst_value['value'] < -30:
                roast.append(f"🤦 **{worst_value['name']}** ({worst_value['club']}) for {worst_value['price']}€ (quota: {worst_value['quotation']}€)? That's not a bid, that's a donation!")

            # Find cheapest player
            cheapest = min(players, key=lambda x: x['price'])
            if cheapest['price'] <= 1:
                roast.append(f"🛒 At least you snagged **{cheapest['name']}** ({cheapest['club']}) for {cheapest['price']}€. One smart move!")

            # Most expensive player
            most_expensive = max(players, key=lambda x: x['price'])
            if most_expensive['price'] > 50:
                roast.append(f"💎 **{most_expensive['name']}** ({most_expensive['club']}) for **{most_expensive['price']}€**! Someone's feeling rich!")

            # Club analysis
            clubs_list = list(stats['clubs_represented'])
            if len(clubs_list) > 0:
                # Count players per club
                club_counts = {}
                for p in players:
                    club = p['club']
                    if club and club != 'Unknown':
                        club_counts[club] = club_counts.get(club, 0) + 1

                # Find favorite club
                if club_counts:
                    fav_club = max(club_counts.items(), key=lambda x: x[1])
                    if fav_club[1] >= 4:
                        roast.append(f"🏟️ **{fav_club[1]} players from {fav_club[0]}**! Are they paying you commission?")
                    elif fav_club[1] >= 3:
                        roast.append(f"👀 {fav_club[1]} players from {fav_club[0]} - someone's a fan!")

            roasts[name] = roast

        return roasts

    def generate_html(self, team_scores, roasts, awards, profiles):
        """Generate fun HTML report"""
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MPG Mercato Roast Report 🔥</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }

        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 1.2em;
            color: #666;
        }

        .section {
            background: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }

        h2 {
            font-size: 2em;
            margin-bottom: 20px;
            color: #667eea;
        }

        .podium {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .podium-item {
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .rank-1 {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            grid-column: span 1;
        }

        .rank-2 {
            background: linear-gradient(135deg, #C0C0C0, #808080);
        }

        .rank-3 {
            background: linear-gradient(135deg, #CD7F32, #8B4513);
        }

        .rank-number {
            font-size: 4em;
            font-weight: bold;
            opacity: 0.3;
            position: absolute;
            top: -10px;
            right: 10px;
        }

        .team-name {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
            position: relative;
            z-index: 1;
        }

        .team-score {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }

        .team-stats {
            font-size: 0.9em;
            opacity: 0.9;
        }

        .rankings-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        .rankings-table th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }

        .rankings-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }

        .rankings-table tr:hover {
            background: #f5f5f5;
        }

        .team-detail {
            border: 2px solid #667eea;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            background: linear-gradient(to right, #f8f9ff, white);
        }

        .roast-box {
            background: #fff3cd;
            border-left: 5px solid #ffc107;
            padding: 15px;
            margin: 15px 0;
            border-radius: 10px;
        }

        .roast-box li {
            margin: 10px 0;
            line-height: 1.6;
        }

        .players-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .player-card {
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            transition: transform 0.2s;
        }

        .player-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .player-card.great-value {
            border-color: #28a745;
            background: #f0fff4;
        }

        .player-card.bad-value {
            border-color: #dc3545;
            background: #fff5f5;
        }

        .player-name {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }

        .player-stats {
            font-size: 0.85em;
            color: #666;
            margin: 5px 0;
        }

        .stat-badge {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
        }

        .chart-container {
            position: relative;
            height: 400px;
            margin: 30px 0;
        }

        @media (max-width: 768px) {
            h1 { font-size: 2em; }
            .podium { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 MPG Mercato Roast Report 🔥</h1>
            <p class="subtitle">Who Spent Wisely? Who Got Absolutely Rinsed? Let's Find Out!</p>
        </div>
'''

        # Podium
        html += '''
        <div class="section">
            <h2>🏆 The Podium</h2>
            <div class="podium">
'''

        for i, team in enumerate(team_scores[:3], 1):
            rank_class = f"rank-{i}"
            medal = ["🥇", "🥈", "🥉"][i-1]
            html += f'''
                <div class="podium-item {rank_class}">
                    <div class="rank-number">{medal}</div>
                    <div class="team-name">{team['name']}</div>
                    <div class="team-score">{team['quality_score']:.0f} pts</div>
                    <div class="team-stats">
                        ⭐ {team['avg_rating']:.2f} avg rating<br>
                        ⚽ {team['total_goals']} goals<br>
                        🏟️ {team['clubs_diversity']} clubs
                    </div>
                </div>
'''

        html += '''
            </div>
        </div>
'''

        # Silly Awards Section
        html += '''
        <div class="section">
            <h2>🏅 Silly Awards Ceremony</h2>
            <div class="awards-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
'''

        for award_key, award in awards.items():
            html += f'''
                <div class="award-card" style="background: linear-gradient(135deg, #f8f9ff, #e8eaff); border: 2px solid #667eea; border-radius: 15px; padding: 20px; text-align: center;">
                    <div style="font-size: 3em; margin-bottom: 10px;">{award['emoji']}</div>
                    <h3 style="color: #667eea; margin-bottom: 10px;">{award['title']}</h3>
                    <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 10px; color: #333;">
                        {award['winner']}
                    </div>
                    <p style="color: #666; font-size: 0.95em;">{award['description']}</p>
                </div>
'''

        html += '''
            </div>
        </div>
'''

        # Psychological Profiles Section
        html += '''
        <div class="section">
            <h2>🧠 Psychological Profiles - Know Your Managers</h2>
            <p style="color: #666; margin-bottom: 30px;">
                Based on bidding behavior, spending patterns, and squad building choices, here's what makes each manager tick...
            </p>
'''

        for team in team_scores:
            name = team['name']
            if name not in profiles:
                continue

            profile = profiles[name]

            html += f'''
            <div class="team-detail" style="margin-bottom: 25px;">
                <h3>{name}</h3>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                    <div>
                        <h4 style="color: #667eea;">Archetype</h4>
                        <p style="font-size: 1.3em; font-weight: bold;">{profile['archetype']}</p>
                        <p style="color: #666; margin-top: 5px;">{profile['strategy']}</p>
                    </div>

                    <div>
                        <h4 style="color: #667eea;">Personality Type</h4>
                        <p style="font-size: 1.3em; font-weight: bold;">{profile.get('personality', '🎯 The Manager')}</p>
                    </div>
                </div>

                <div style="margin-top: 20px;">
                    <h4 style="color: #667eea;">Key Traits</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
'''

            for trait in profile['traits']:
                html += f'''
                        <span class="stat-badge" style="background: #764ba2; padding: 5px 12px; font-size: 0.9em;">{trait}</span>
'''

            html += f'''
                    </div>
                </div>

                <div style="margin-top: 20px; padding: 15px; background: #f8f9ff; border-radius: 10px;">
                    <h4 style="color: #667eea; margin-bottom: 10px;">Behavioral Analysis</h4>
                    <p style="color: #333; line-height: 1.6;">{profile['description']}</p>
                </div>

                <div style="margin-top: 15px; padding: 15px; background: #fff3cd; border-radius: 10px; border-left: 4px solid #ffc107;">
                    <p style="color: #856404; margin: 0;"><strong>💰 Money Philosophy:</strong> {profile['emotional_state']}</p>
                </div>
            </div>
'''

        html += '''
        </div>
'''

        # Most Contested Players Section
        html += '''
        <div class="section">
            <h2>🔥 Most Contested Auctions - Battle Royale!</h2>
            <p style="color: #666; margin-bottom: 20px;">
                These players had everyone fighting for them. Who won the bidding wars?
            </p>
'''

        # Sort contested players by number of bidders
        top_contested = sorted(self.contested_players, key=lambda x: x['total_bidders'], reverse=True)[:15]

        if top_contested:
            html += '''
            <table class="rankings-table">
                <thead>
                    <tr>
                        <th>Player</th>
                        <th>Club</th>
                        <th>Bidders</th>
                        <th>Winner</th>
                        <th>Price</th>
                        <th>Quota</th>
                        <th>Value</th>
                        <th>Rating</th>
                        <th>Goals</th>
                        <th>Analysis</th>
                    </tr>
                </thead>
                <tbody>
'''

            for contest in top_contested:
                player = contest['player']
                winner = contest['winner']
                total_bidders = contest['total_bidders']

                value_color = 'green' if player['value'] >= 0 else 'red'
                smart_buy = "🧠 Smart!" if player['value'] >= -5 else "😬 Overpaid" if player['value'] < -15 else "📊 Fair"

                # Determine if winner got a good deal
                if player['avgRating'] > 5.5 and player['value'] >= -5:
                    analysis = "✅ Great win!"
                elif player['avgRating'] > 5.0:
                    analysis = "👍 Good pickup"
                elif player['value'] < -20:
                    analysis = "💸 Too much!"
                else:
                    analysis = "🤷 Decent"

                html += f'''
                    <tr>
                        <td><strong>{player['name']}</strong></td>
                        <td>{player['club']}</td>
                        <td><strong style="color: #667eea; font-size: 1.2em;">{total_bidders}</strong> teams</td>
                        <td><strong>{winner}</strong></td>
                        <td>{player['price']}€</td>
                        <td>{player['quotation']}€</td>
                        <td style="color: {value_color}; font-weight: bold;">{player['value']:+}€</td>
                        <td>⭐ {player['avgRating']:.2f}</td>
                        <td>⚽ {player['totalGoals']}</td>
                        <td>{analysis}</td>
                    </tr>
'''

            html += '''
                </tbody>
            </table>
'''

            # Add summary stats
            total_contested = len([x for x in self.contested_players if x['total_bidders'] >= 3])
            avg_bidders = sum(x['total_bidders'] for x in self.contested_players) / len(self.contested_players) if self.contested_players else 0

            # Who won the most contested battles?
            winner_counts = {}
            for contest in self.contested_players:
                winner_id = contest['winner_id']
                winner_counts[winner_id] = winner_counts.get(winner_id, 0) + 1

            html += f'''
            <div style="margin-top: 30px; padding: 20px; background: #f8f9ff; border-radius: 10px;">
                <h3>📊 Bidding War Statistics</h3>
                <p><strong>{total_contested}</strong> players had 3+ bidders competing for them!</p>
                <p>Average bidders per contested player: <strong>{avg_bidders:.1f}</strong></p>

                <h4 style="margin-top: 20px;">🏆 Kings of Contested Auctions (Who Won the Most Battles)</h4>
                <ul style="font-size: 1.1em;">
'''

            sorted_winners = sorted(winner_counts.items(), key=lambda x: x[1], reverse=True)
            for i, (winner_id, count) in enumerate(sorted_winners[:5], 1):
                winner_name = self.teams.get(winner_id, {}).get('name', winner_id[-6:])
                # Calculate their success rate on contested players
                wins = count
                total_contested_by_team = sum(1 for c in self.contested_players if c['winner_id'] == winner_id)

                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1] if i <= 5 else "•"
                html += f'''
                    <li>{emoji} <strong>{winner_name}</strong>: Won <strong>{wins}</strong> contested auctions - {"Bidding warrior!" if wins >= 5 else "Competitive player" if wins >= 3 else "Careful selector"}</li>
'''

            html += '''
                </ul>
            </div>
        </div>
'''
        else:
            html += '''
                <p>No highly contested auctions found.</p>
            </div>
'''

        # Full Rankings Table
        html += '''
        <div class="section">
            <h2>📊 Complete Rankings</h2>
            <table class="rankings-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Team</th>
                        <th>Quality Score</th>
                        <th>Avg Rating</th>
                        <th>Avg Points</th>
                        <th>Goals</th>
                        <th>Players</th>
                        <th>Clubs</th>
                        <th>Value Eff.</th>
                    </tr>
                </thead>
                <tbody>
'''

        for i, team in enumerate(team_scores, 1):
            value_color = 'red' if team['value_efficiency'] < -10 else 'orange' if team['value_efficiency'] < -5 else 'green'
            html += f'''
                    <tr>
                        <td><strong>{i}</strong></td>
                        <td><strong>{team['name']}</strong></td>
                        <td>{team['quality_score']:.0f}</td>
                        <td>{team['avg_rating']:.2f}</td>
                        <td>{team['avg_points']:.1f}</td>
                        <td>{team['total_goals']}</td>
                        <td>{team['num_players']}</td>
                        <td>{team['clubs_diversity']}</td>
                        <td style="color: {value_color}; font-weight: bold;">{team['value_efficiency']:+.1f}€</td>
                    </tr>
'''

        html += '''
                </tbody>
            </table>
        </div>
'''

        # Charts
        html += '''
        <div class="section">
            <h2>📈 Visual Analysis</h2>
            <div class="chart-container">
                <canvas id="qualityChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="valueChart"></canvas>
            </div>
        </div>
'''

        # Team Details with Roasts
        html += '''
        <div class="section">
            <h2>🎯 Team-by-Team Roast</h2>
'''

        for i, team in enumerate(team_scores, 1):
            name = team['name']
            team_roasts = roasts.get(name, [])

            html += f'''
            <div class="team-detail">
                <h3>#{i} - {name}</h3>
                <p><strong>Quality Score:</strong> {team['quality_score']:.0f} |
                   <strong>Avg Rating:</strong> {team['avg_rating']:.2f} |
                   <strong>Total Goals:</strong> {team['total_goals']} |
                   <strong>Clubs:</strong> {team['clubs_diversity']}</p>

                <div class="roast-box">
                    <strong>🔥 The Roast:</strong>
                    <ul>
'''

            for roast in team_roasts:
                html += f'<li>{roast}</li>'

            html += '''
                    </ul>
                </div>

                <h4>Club Diversity:</h4>
                <p>
'''

            # Add club breakdown
            club_counts = {}
            for p in team['stats']['players_won']:
                club = p['club']
                if club and club != 'Unknown':
                    club_counts[club] = club_counts.get(club, 0) + 1

            if club_counts:
                sorted_clubs = sorted(club_counts.items(), key=lambda x: x[1], reverse=True)
                club_text = ', '.join([f"<strong>{club}</strong> ({count})" for club, count in sorted_clubs])
                html += f"{club_text}"

            html += '''
                </p>

                <h4>Squad:</h4>
                <div class="players-grid">
'''

            # Sort players by position (GK -> DEF -> MID -> FWD), then by value
            players = sorted(team['stats']['players_won'], key=lambda x: (x['position'], -x['value']))

            # Group by position
            position_headers = {1: '🧤 Goalkeepers', 2: '🛡️ Defenders', 3: '⚙️ Midfielders', 4: '⚽ Forwards'}
            position_badges = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}
            current_position = None

            for player in players:
                # Add position header when position changes
                if player['position'] != current_position:
                    current_position = player['position']
                    position_label = position_headers.get(current_position, 'Unknown')
                    html += f'''
                </div>
                <h4 style="margin-top: 20px; color: #667eea;">{position_label}</h4>
                <div class="players-grid">
'''

                card_class = 'great-value' if player['value'] > 0 else 'bad-value' if player['value'] < -10 else ''
                pos_name = position_badges.get(player['position'], 'UNK')

                html += f'''
                    <div class="player-card {card_class}">
                        <div class="player-name">{player['name']}</div>
                        <div class="player-stats">
                            <span class="stat-badge">{pos_name}</span>
                            <span class="stat-badge" style="background: #28a745;">{player['club']}</span>
                            <span class="stat-badge">{player['price']}€</span>
                            <span class="stat-badge" style="background: {'green' if player['value'] >= 0 else 'red'}">
                                {player['value']:+}€
                            </span>
                        </div>
                        <div class="player-stats">
                            ⭐ {player['avgRating']:.2f} rating |
                            📊 {player['avgPoints']:.1f}pts |
                            ⚽ {player['totalGoals']}g
                        </div>
                        <div class="player-stats">
                            🏃 {player['totalMatches']} matches played
                        </div>
                    </div>
'''

            html += '''
                </div>
            </div>
'''

        html += '''
        </div>
'''

        # JavaScript for charts
        team_names = [t['name'][:15] + '...' if len(t['name']) > 15 else t['name'] for t in team_scores]
        quality_scores = [t['quality_score'] for t in team_scores]
        value_effs = [abs(t['value_efficiency']) for t in team_scores]

        html += f'''
        <script>
            // Quality Score Chart
            const qualityCtx = document.getElementById('qualityChart').getContext('2d');
            new Chart(qualityCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(team_names)},
                    datasets: [{{
                        label: 'Team Quality Score',
                        data: {json.dumps(quality_scores)},
                        backgroundColor: 'rgba(102, 126, 234, 0.8)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Quality Score'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Team Quality Scores (Higher = Better Squad)',
                            font: {{ size: 18 }}
                        }}
                    }}
                }}
            }});

            // Value Efficiency Chart
            const valueCtx = document.getElementById('valueChart').getContext('2d');
            new Chart(valueCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(team_names)},
                    datasets: [{{
                        label: 'Average Overpay per Player (€)',
                        data: {json.dumps(value_effs)},
                        backgroundColor: 'rgba(220, 53, 69, 0.8)',
                        borderColor: 'rgba(220, 53, 69, 1)',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Overpaid Amount (€)'
                            }}
                        }}
                    }},
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Who Overpaid the Most? (Lower = Better Value)',
                            font: {{ size: 18 }}
                        }}
                    }}
                }}
            }});
        </script>
    </div>
</body>
</html>
'''

        return html

    def generate(self, output_file="mpg_roast_report.html"):
        """Generate the complete report"""
        print("="*60)
        print("MPG FUN REPORT GENERATOR")
        print("="*60 + "\n")

        self.load_data()
        self.analyze_auctions()

        team_scores = self.calculate_team_scores()
        awards = self.calculate_silly_awards(team_scores)
        roasts = self.generate_roasts(team_scores)
        profiles = self.generate_psychological_profiles(team_scores)

        html = self.generate_html(team_scores, roasts, awards, profiles)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Report generated: {output_file}")
        print(f"📂 Open it in your browser to see the roast!\n")


if __name__ == "__main__":
    generator = FunReportGenerator("mpg_auction_data.json")
    generator.generate()
