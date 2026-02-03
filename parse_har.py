#!/usr/bin/env python3
"""
Parse Chrome HAR (HTTP Archive) file to extract MPG API data
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def parse_har_file(har_path):
    """Parse HAR file and extract MPG API calls and responses"""
    print(f"Reading HAR file: {har_path}")

    try:
        with open(har_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except Exception as e:
        print(f"Error reading HAR file: {e}")
        return None

    entries = har_data.get('log', {}).get('entries', [])
    print(f"Found {len(entries)} network requests")

    mpg_data = {
        "scrape_timestamp": datetime.now().isoformat(),
        "api_calls": [],
        "responses": {}
    }

    # Extract MPG API calls
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        url = request.get('url', '')

        # Filter for MPG API calls
        if 'api.mpg.football' in url or ('mpg.football' in url and '/api/' in url):
            # Extract response content
            content = response.get('content', {})
            response_text = content.get('text', '')

            # Try to parse JSON response
            response_data = None
            if response_text:
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = response_text

            call_info = {
                "url": url,
                "method": request.get('method'),
                "status": response.get('status'),
                "statusText": response.get('statusText'),
                "timestamp": entry.get('startedDateTime'),
                "time": entry.get('time'),
                "response_size": content.get('size', 0)
            }

            mpg_data["api_calls"].append(call_info)

            # Store response data with a clean key
            clean_url = url.split('?')[0].replace('https://api.mpg.football/', '')
            if response_data:
                mpg_data["responses"][clean_url] = response_data

    print(f"\n✓ Extracted {len(mpg_data['api_calls'])} MPG API calls")
    print(f"✓ Captured {len(mpg_data['responses'])} responses with data")

    return mpg_data


def analyze_data(data):
    """Analyze the extracted data and print summary"""
    print("\n" + "="*60)
    print("API ENDPOINTS FOUND")
    print("="*60)

    for call in data['api_calls']:
        url = call['url'].split('?')[0]
        status = call['status']
        method = call['method']
        print(f"  [{status}] {method:6s} {url}")

    print("\n" + "="*60)
    print("RESPONSES WITH DATA")
    print("="*60)

    for endpoint, response in data['responses'].items():
        if isinstance(response, dict):
            keys = list(response.keys())[:5]  # First 5 keys
            print(f"\n  {endpoint}")
            print(f"    Type: {type(response).__name__}")
            if keys:
                print(f"    Keys: {', '.join(keys)}")
        elif isinstance(response, list):
            print(f"\n  {endpoint}")
            print(f"    Type: List with {len(response)} items")


def save_data(data, output_path="mpg_auction_data.json"):
    """Save parsed data to JSON file"""
    output = Path(output_path)

    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✓ Data saved to: {output.absolute()}")
    print(f"  File size: {output.stat().st_size / 1024:.2f} KB")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_har.py <path_to_har_file>")
        print("\nTo generate a HAR file:")
        print("1. Open Chrome DevTools (Cmd+Option+I)")
        print("2. Go to Network tab")
        print("3. Navigate to your MPG league page")
        print("4. Right-click in Network tab → 'Save all as HAR with content'")
        return 1

    har_path = sys.argv[1]

    if not Path(har_path).exists():
        print(f"Error: File not found: {har_path}")
        return 1

    # Parse HAR file
    data = parse_har_file(har_path)

    if not data:
        print("Failed to parse HAR file")
        return 1

    # Analyze and display summary
    analyze_data(data)

    # Save to JSON
    save_data(data)

    print("\n✓ Extraction completed successfully!")
    print("\nYou can now analyze the data in mpg_auction_data.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
