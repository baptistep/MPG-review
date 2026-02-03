#!/usr/bin/env python3
"""
MPG Fantasy Football Auction Data Scraper
Extracts trading/auction data from MPG using your Chrome session
"""

import json
import sys
import browser_cookie3
import requests
from datetime import datetime
from pathlib import Path


class MPGScraper:
    def __init__(self):
        self.base_url = "https://api.mpg.football/api"
        self.session = requests.Session()
        self.league_id = "mpg_league_1XQHDZXWT"
        self.division_id = "mpg_division_1XQHDZXWT_23_1"

    def load_chrome_cookies(self):
        """Extract cookies from Chrome browser"""
        try:
            print("Extracting cookies from Chrome...")
            cookies = browser_cookie3.chrome(domain_name='mpg.football')
            for cookie in cookies:
                self.session.cookies.set(cookie.name, cookie.value)
            print(f"✓ Loaded {len(self.session.cookies)} cookies")
            return True
        except Exception as e:
            print(f"Error loading cookies: {e}")
            print("\nTip: Make sure Chrome is closed or try running with sudo/admin privileges")
            return False

    def get_league_info(self):
        """Get general league information"""
        url = f"{self.base_url}/league/{self.league_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching league info: {e}")
            return None

    def get_division_info(self):
        """Get division details"""
        url = f"{self.base_url}/division/{self.division_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching division info: {e}")
            return None

    def get_mercato_data(self):
        """Get auction/trading market data"""
        # Try multiple potential endpoints
        endpoints = [
            f"{self.base_url}/division/{self.division_id}/mercato",
            f"{self.base_url}/division/{self.division_id}/trading",
            f"{self.base_url}/league/{self.league_id}/mercato",
            f"{self.base_url}/championship-mercato/{self.division_id}",
        ]

        for endpoint in endpoints:
            try:
                print(f"Trying endpoint: {endpoint}")
                response = self.session.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ Successfully fetched mercato data")
                    return data
            except Exception as e:
                print(f"  Failed: {e}")
                continue

        return None

    def get_championship_players(self):
        """Get all available players in the championship"""
        url = f"{self.base_url}/championship/1/stats"  # 1 is typically Ligue 1
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching championship players: {e}")
            return None

    def scrape_all_data(self):
        """Main scraping function"""
        print("\n" + "="*60)
        print("MPG Auction Data Scraper")
        print("="*60 + "\n")

        if not self.load_chrome_cookies():
            return None

        all_data = {
            "scrape_timestamp": datetime.now().isoformat(),
            "league_id": self.league_id,
            "division_id": self.division_id,
        }

        print("\nFetching league information...")
        league_info = self.get_league_info()
        if league_info:
            all_data["league"] = league_info
            print("✓ League info retrieved")

        print("\nFetching division information...")
        division_info = self.get_division_info()
        if division_info:
            all_data["division"] = division_info
            print("✓ Division info retrieved")

        print("\nFetching mercato/auction data...")
        mercato_data = self.get_mercato_data()
        if mercato_data:
            all_data["mercato"] = mercato_data
            print("✓ Mercato data retrieved")

        print("\nFetching championship player stats...")
        players_data = self.get_championship_players()
        if players_data:
            all_data["players"] = players_data
            print("✓ Player stats retrieved")

        return all_data

    def save_data(self, data, filename="mpg_auction_data.json"):
        """Save scraped data to JSON file"""
        if not data:
            print("\nNo data to save!")
            return

        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*60}")
        print(f"✓ Data saved to: {output_path.absolute()}")
        print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")
        print(f"{'='*60}\n")

        # Print summary
        if "mercato" in data:
            print("Summary:")
            print(f"  - Mercato data: Available")
        if "league" in data:
            print(f"  - League info: Available")
        if "division" in data:
            print(f"  - Division info: Available")
        if "players" in data:
            print(f"  - Player stats: Available")


def main():
    scraper = MPGScraper()
    data = scraper.scrape_all_data()

    if data:
        scraper.save_data(data)
        print("\n✓ Scraping completed successfully!")
        return 0
    else:
        print("\n✗ Scraping failed - please check errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
