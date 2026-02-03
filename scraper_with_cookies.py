#!/usr/bin/env python3
"""
MPG Scraper using Selenium with imported cookies
Opens a fresh browser and injects your Chrome cookies
"""

import json
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import browser_cookie3


class MPGCookieScraper:
    def __init__(self):
        self.driver = None
        self.url = "https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading?modal=mercatoBackstage&initialDivisionId=mpg_division_1XQHDZXWT_23_1"

    def setup_driver(self):
        """Setup Chrome driver with basic options"""
        print("Setting up Chrome driver...")

        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✓ Chrome driver initialized")
            return True
        except Exception as e:
            print(f"Error setting up driver: {e}")
            return False

    def inject_cookies(self):
        """Extract cookies from Chrome and inject them into Selenium"""
        print("\nLoading cookies from Chrome...")

        try:
            # First navigate to the domain
            self.driver.get("https://mpg.football")
            time.sleep(2)

            # Get cookies from Chrome
            cookies = browser_cookie3.chrome(domain_name='mpg.football')

            # Inject each cookie
            count = 0
            for cookie in cookies:
                try:
                    cookie_dict = {
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'secure': cookie.secure
                    }
                    if cookie.expires:
                        cookie_dict['expiry'] = int(cookie.expires)

                    self.driver.add_cookie(cookie_dict)
                    count += 1
                except Exception as e:
                    print(f"  Warning: Could not add cookie {cookie.name}: {e}")

            print(f"✓ Injected {count} cookies")
            return True

        except Exception as e:
            print(f"Error injecting cookies: {e}")
            return False

    def capture_network_traffic(self):
        """Capture all network requests from performance logs"""
        print("\nCapturing network traffic...")

        # Get performance logs
        logs = self.driver.get_log('performance')

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
                    if 'api.mpg.football' in url or ('mpg.football' in url and '/api/' in url):
                        api_calls.append({
                            'url': url,
                            'method': response.get('method'),
                            'status': response.get('status'),
                            'requestId': params.get('requestId')
                        })
            except:
                continue

        return api_calls

    def extract_page_data(self):
        """Try to extract data from JavaScript on the page"""
        print("Extracting data from page...")

        data = {}

        scripts = [
            # Try localStorage
            ("localStorage", "return JSON.parse(JSON.stringify(localStorage));"),

            # Try sessionStorage
            ("sessionStorage", "return JSON.parse(JSON.stringify(sessionStorage));"),

            # Try to get any global MPG data
            ("window_mpg", """
                var data = {};
                if (window.mpgData) data.mpgData = window.mpgData;
                if (window.__INITIAL_STATE__) data.initialState = window.__INITIAL_STATE__;
                if (window.__PRELOADED_STATE__) data.preloadedState = window.__PRELOADED_STATE__;
                return Object.keys(data).length > 0 ? data : null;
            """),
        ]

        for name, script in scripts:
            try:
                result = self.driver.execute_script(script)
                if result:
                    data[name] = result
                    print(f"  ✓ Extracted {name}")
            except Exception as e:
                print(f"  ✗ Failed {name}: {e}")

        return data

    def scrape(self):
        """Main scraping method"""
        print("\n" + "="*60)
        print("MPG Auction Data Scraper (Cookie-Based)")
        print("="*60 + "\n")

        if not self.setup_driver():
            return None

        try:
            # Inject cookies first
            if not self.inject_cookies():
                print("Warning: Could not inject cookies, page may not be authenticated")

            # Now navigate to the target page
            print(f"\nNavigating to: {self.url}")
            self.driver.get(self.url)

            # Wait for page to load
            print("Waiting for page to load...")
            time.sleep(10)  # Give it time to load and make API calls

            # Capture network traffic
            api_calls = self.capture_network_traffic()
            print(f"✓ Captured {len(api_calls)} API calls")

            # Extract page data
            page_data = self.extract_page_data()

            # Compile results
            result = {
                "scrape_timestamp": datetime.now().isoformat(),
                "url": self.url,
                "api_calls": api_calls,
                "page_data": page_data,
            }

            # Print discovered API endpoints
            if api_calls:
                print("\n" + "="*60)
                print("DISCOVERED API ENDPOINTS")
                print("="*60)
                unique_endpoints = set([call['url'].split('?')[0] for call in api_calls])
                for endpoint in sorted(unique_endpoints):
                    print(f"  {endpoint}")

            return result

        except Exception as e:
            print(f"\nError during scraping: {e}")
            import traceback
            traceback.print_exc()
            return None

        finally:
            if self.driver:
                print("\nClosing browser...")
                self.driver.quit()

    def save_data(self, data, filename="mpg_auction_data.json"):
        """Save scraped data"""
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
    scraper = MPGCookieScraper()
    data = scraper.scrape()

    if data:
        scraper.save_data(data)
        print("\n✓ Scraping completed successfully!")
        return 0
    else:
        print("\n✗ Scraping failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
