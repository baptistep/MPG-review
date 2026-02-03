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

                # Process lost bids - these teams bid but didn't win
                for lost_bid in lost_bids:
                    loser_id = lost_bid.get('teamId')
                    if loser_id:
                        self.team_stats[loser_id]['total_bids'] += 1

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

            # Calculate spending by position
            spending_by_position = {
                'GK': {'spent': 0, 'count': 0},
                'DEF': {'spent': 0, 'count': 0},
                'MID': {'spent': 0, 'count': 0},
                'FWD': {'spent': 0, 'count': 0}
            }

            position_map = {1: 'GK', 2: 'DEF', 3: 'MID', 4: 'FWD'}

            for player in stats['players_won']:
                pos = position_map.get(player['position'], 'UNK')
                if pos in spending_by_position:
                    spending_by_position[pos]['spent'] += player['price']
                    spending_by_position[pos]['count'] += 1

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
                'spending_by_position': spending_by_position,
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
    <title>MPG Mercato Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        h1 {
            font-size: 2.2em;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 600;
        }

        .subtitle {
            font-size: 1em;
            color: #7f8c8d;
        }

        .section {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        h2 {
            font-size: 1.6em;
            margin-bottom: 20px;
            color: #2c3e50;
            font-weight: 600;
        }

        h3 {
            font-size: 1.3em;
            margin: 20px 0 15px 0;
            color: #34495e;
            font-weight: 600;
        }

        .podium {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }

        .podium-item {
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            background: #f8f9fa;
            border: 2px solid #e9ecef;
        }

        .rank-1 { border-color: #ffd700; background: #fffbeb; }
        .rank-2 { border-color: #c0c0c0; background: #f8f9fa; }
        .rank-3 { border-color: #cd7f32; background: #fff5eb; }

        .team-name {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 8px;
            color: #2c3e50;
        }

        .team-score {
            font-size: 1.8em;
            font-weight: 700;
            color: #3498db;
            margin: 8px 0;
        }

        .team-stats {
            font-size: 0.9em;
            color: #7f8c8d;
            line-height: 1.8;
        }

        .rankings-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        .rankings-table th {
            background: #ecf0f1;
            color: #2c3e50;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
        }

        .rankings-table td {
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 0.95em;
        }

        .rankings-table tr:hover {
            background: #f8f9fa;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            margin: 8px 0;
            background: #f8f9fa;
            border-radius: 8px;
        }

        .stat-label {
            font-weight: 600;
            color: #2c3e50;
        }

        .stat-value {
            color: #3498db;
            font-weight: 600;
        }

        .profile-card {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #3498db;
        }

        .profile-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .profile-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
        }

        .archetype {
            font-size: 1.1em;
            color: #3498db;
        }

        .trait-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 10px 0;
        }

        .trait-badge {
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.85em;
        }

        .chart-container {
            position: relative;
            height: 350px;
            margin: 25px 0;
        }

        .position-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }

        .position-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .position-label {
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 8px;
        }

        .position-value {
            font-size: 1.6em;
            font-weight: 700;
            color: #3498db;
        }

        .position-sub {
            font-size: 0.85em;
            color: #95a5a6;
            margin-top: 4px;
        }

        @media (max-width: 768px) {
            h1 { font-size: 1.8em; }
            .podium { grid-template-columns: 1fr; }
            .position-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>MPG Mercato Analysis</h1>
            <p class="subtitle">Squad Building & Investment Strategy Breakdown</p>
        </div>
'''

        # Podium
        html += '''
        <div class="section">
            <h2>Top 3 Teams</h2>
            <div class="podium">
'''

        for i, team in enumerate(team_scores[:3], 1):
            rank_class = f"rank-{i}"
            medal = ["🥇", "🥈", "🥉"][i-1]
            html += f'''
                <div class="podium-item {rank_class}">
                    <div class="team-name">{medal} {team['name']}</div>
                    <div class="team-score">{team['quality_score']:.0f}</div>
                    <div class="team-stats">
                        Rating: {team['avg_rating']:.2f} • Goals: {team['total_goals']} • Win Rate: {team['win_rate']:.0f}%
                    </div>
                </div>
'''

        html += '''
            </div>
        </div>
'''

        # Position Spending Analysis
        html += '''
        <div class="section">
            <h2>Investment Strategy by Position</h2>
            <p style="color: #7f8c8d; margin-bottom: 20px;">How much did each team invest in different positions?</p>
'''

        for team in team_scores:
            spending = team['spending_by_position']
            total_spent = team['stats']['total_spent']

            html += f'''
            <div class="profile-card" style="border-left-color: #3498db;">
                <div class="profile-header">
                    <div class="profile-title">{team['name']}</div>
                    <div style="color: #7f8c8d;">Total: {total_spent}€</div>
                </div>
                <div class="position-grid">
'''

            for pos in ['GK', 'DEF', 'MID', 'FWD']:
                spent = spending[pos]['spent']
                count = spending[pos]['count']
                pct = (spent / total_spent * 100) if total_spent > 0 else 0
                avg = (spent / count) if count > 0 else 0

                emoji = {'GK': '🧤', 'DEF': '🛡️', 'MID': '⚙️', 'FWD': '⚽'}

                html += f'''
                    <div class="position-card">
                        <div class="position-label">{emoji[pos]} {pos}</div>
                        <div class="position-value">{spent}€</div>
                        <div class="position-sub">{pct:.0f}% • {count} players • {avg:.0f}€ avg</div>
                    </div>
'''

            html += '''
                </div>
            </div>
'''

        html += '''
        </div>
'''

        # Psychological Profiles Section (Simplified)
        html += '''
        <div class="section">
            <h2>Manager Profiles</h2>
            <p style="color: #7f8c8d; margin-bottom: 20px;">Bidding behavior & squad building strategy</p>
'''

        for team in team_scores:
            name = team['name']
            if name not in profiles:
                continue

            profile = profiles[name]

            html += f'''
            <div class="profile-card">
                <div class="profile-header">
                    <div class="profile-title">{name}</div>
                    <div class="archetype">{profile['archetype']}</div>
                </div>
                <p style="color: #7f8c8d; margin: 10px 0;">{profile['strategy']}</p>
                <div class="stat-row" style="margin-top: 15px;">
                    <span class="stat-label">Personality</span>
                    <span class="stat-value">{profile.get('personality', '🎯 The Manager')}</span>
                </div>
            </div>
'''

        html += '''
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
