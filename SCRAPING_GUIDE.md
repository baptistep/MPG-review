# MPG Auction Data Scraping Guide

## Option 1: Manual Export (Recommended - Easiest)

This is the simplest and most reliable method.

### Steps:

1. **Open Chrome DevTools**
   - Open Chrome and navigate to your MPG league page:
     https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading
   - Press `Cmd+Option+I` (or right-click → Inspect)
   - Click on the "Network" tab

2. **Filter for API Calls**
   - In the filter box, type: `api.mpg`
   - Reload the page (`Cmd+R`) to capture all network requests
   - Navigate to the trading/auction section if needed

3. **Export Network Data**
   - Right-click anywhere in the Network tab
   - Select "Save all as HAR with content"
   - Save the file as `mpg_network_data.har`

4. **Run the parser script**
   ```bash
   python3 parse_har.py mpg_network_data.har
   ```

---

## Option 2: Automated with Selenium

Uses browser automation to capture data automatically.

### Prerequisites:
```bash
# Install ChromeDriver
brew install chromedriver

# Install Python dependencies
pip3 install -r requirements.txt
```

### Run:
```bash
python3 scraper_selenium.py
```

**Note:** You'll need to close all Chrome windows first for this to work properly.

---

## Option 3: Manual API Inspection (For developers)

If you want to understand the API structure:

1. Open DevTools Network tab
2. Filter by `api.mpg`
3. Click on each request to see:
   - Request URL
   - Request headers (look for authentication)
   - Response data

Common MPG API patterns:
- `/api/league/{league_id}`
- `/api/division/{division_id}`
- `/api/mercato/...`
- `/api/championship-trading/...`

---

## Next Steps

Once we have the data, we'll create an analysis script to:
- Identify all auction participants
- Track bidding patterns
- Calculate who overpaid/underpaid
- Identify the best auction strategists
- Generate visualizations
