#!/usr/bin/env python3
"""
MPG Fantasy Football Auction Data Scraper using Selenium
Uses your existing Chrome profile to access the page and capture network data
"""

import json
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import subprocess


def get_chrome_user_data_dir():
    """Get the Chrome user data directory for macOS"""
    return str(Path.home() / "Library/Application Support/Google/Chrome")


class MPGSeleniumScraper:
    def __init__(self):
        self.driver = None
        self.network_logs = []
        self.api_responses = {}

    def setup_driver(self):
        """Setup Chrome driver with existing profile"""
        print("Setting up Chrome driver...")

        chrome_options = Options()

        # Use existing Chrome profile
        user_data_dir = get_chrome_user_data_dir()
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")
        chrome_options.add_argument("profile-directory=Default")

        # Enable performance logging to capture network traffic
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        # Optional: run in headless mode (comment out to see browser)
        # chrome_options.add_argument("--headless=new")

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Chrome driver initialized")
            return True
        except Exception as e:
            print(f"Error setting up driver: {e}")
            print("\nMake sure ChromeDriver is installed:")
            print("  brew install chromedriver")
            return False

    def load_page_and_capture_requests(self, url, wait_time=10):
        """Load the MPG page and capture all network requests"""
        print(f"\nLoading page: {url}")

        try:
            self.driver.get(url)
            print("✓ Page loaded, waiting for content...")

            # Wait for page to load
            time.sleep(wait_time)

            # Extract performance logs
            logs = self.driver.get_log('performance')

            print(f"✓ Captured {len(logs)} network events")

            return logs
        except Exception as e:
            print(f"Error loading page: {e}")
            return []

    def parse_network_logs(self, logs):
        """Parse performance logs to extract API calls and responses"""
        api_calls = []

        for entry in logs:
            try:
                log = json.loads(entry['message'])
                message = log['message']
                method = message.get('method')

                # Look for network responses
                if method == 'Network.responseReceived':
                    params = message.get('params', {})
                    response = params.get('response', {})
                    url = response.get('url', '')

                    # Filter for MPG API calls
                    if 'api.mpg.football' in url or 'mpg.football' in url:
                        api_calls.append({
                            'url': url,
                            'method': response.get('method'),
                            'status': response.get('status'),
                            'requestId': params.get('requestId')
                        })

            except Exception as e:
                continue

        return api_calls

    def execute_script_to_get_data(self):
        """Execute JavaScript to extract data from the page"""
        print("\nExtracting data via JavaScript...")

        scripts = {
            # Try to get data from window/global objects
            'window_data': """
                return {
                    localStorage: {...localStorage},
                    sessionStorage: {...sessionStorage},
                    // Try common global variables
                    __INITIAL_STATE__: window.__INITIAL_STATE__,
                    __PRELOADED_STATE__: window.__PRELOADED_STATE__,
                    mpgData: window.mpgData,
                    appData: window.appData
                };
            """,

            # Try to get Redux store if available
            'redux_store': """
                if (window.store) {
                    return window.store.getState();
                }
                return null;
            """,

            # Get Angular scope if available
            'angular_data': """
                if (window.angular) {
                    var elem = document.querySelector('[ng-app]');
                    if (elem) {
                        return angular.element(elem).scope();
                    }
                }
                return null;
            """,
        }

        extracted_data = {}

        for name, script in scripts.items():
            try:
                result = self.driver.execute_script(script)
                if result:
                    extracted_data[name] = result
                    print(f"  ✓ Extracted {name}")
            except Exception as e:
                print(f"  ✗ Failed to extract {name}: {e}")

        return extracted_data

    def scrape_mpg(self, url):
        """Main scraping method"""
        print("\n" + "="*60)
        print("MPG Auction Data Scraper (Selenium)")
        print("="*60 + "\n")

        if not self.setup_driver():
            return None

        try:
            # Load the page
            logs = self.load_page_and_capture_requests(url, wait_time=15)

            # Parse network logs
            api_calls = self.parse_network_logs(logs)
            print(f"\n✓ Found {len(api_calls)} API calls")

            # Print unique API endpoints
            unique_endpoints = set([call['url'].split('?')[0] for call in api_calls])
            print("\nDiscovered API endpoints:")
            for endpoint in sorted(unique_endpoints):
                if 'api.mpg' in endpoint:
                    print(f"  - {endpoint}")

            # Try to extract data from page
            page_data = self.execute_script_to_get_data()

            # Compile all data
            all_data = {
                "scrape_timestamp": datetime.now().isoformat(),
                "url": url,
                "api_calls": api_calls,
                "page_data": page_data,
            }

            return all_data

        except Exception as e:
            print(f"\nError during scraping: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()

    def save_data(self, data, filename="mpg_auction_data_selenium.json"):
        """Save scraped data to JSON file"""
        if not data:
            print("\nNo data to save!")
            return

        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n{'='*60}")
        print(f"✓ Data saved to: {output_path.absolute()}")
        print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")
        print(f"{'='*60}\n")


def main():
    url = "https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading?modal=mercatoBackstage&initialDivisionId=mpg_division_1XQHDZXWT_23_1"

    scraper = MPGSeleniumScraper()
    data = scraper.scrape_mpg(url)

    if data:
        scraper.save_data(data)
        print("\n✓ Scraping completed successfully!")
        print("\nNext steps:")
        print("1. Check mpg_auction_data_selenium.json for API endpoints")
        print("2. We can then create a targeted scraper for those endpoints")
        return 0
    else:
        print("\n✗ Scraping failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
