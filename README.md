# MPG Fantasy Football Auction Data Scraper & Analyzer

Extract and analyze auction/trading data from your MPG fantasy football league to understand bidding patterns and identify the best strategists.

## 🚀 Quick Start (Recommended Method)

### Step 1: Extract Data from Browser

1. Open your MPG league trading page in Chrome:
   ```
   https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading
   ```

2. Open Chrome Developer Console:
   - **Mac:** `Cmd + Option + J`
   - **Windows/Linux:** `Ctrl + Shift + J`

3. Open `extract_data.js` in a text editor, copy ALL the code

4. Paste into the console and press Enter

5. **IMPORTANT:** You have 10 seconds to navigate around the page:
   - Click on different auctions
   - Open player details
   - Navigate through tabs (active/completed auctions)
   - The more you interact, the more data it captures!

6. After 10 seconds, `mpg_auction_data.json` will download to your Downloads folder

7. Move it to this directory:
   ```bash
   mv ~/Downloads/mpg_auction_data.json /Users/baptiste/Desktop/Apps/MPG/
   ```

### Step 2: Analyze the Data

```bash
cd /Users/baptiste/Desktop/Apps/MPG
python3 analyze_auctions.py mpg_auction_data.json
```

The script will:
- 📊 Identify all bidders and their performance
- 🎯 Calculate win rates and spending patterns
- 💰 Find who got the best value
- 📈 Generate a detailed performance report

---

## 📁 Files in This Project

| File | Purpose |
|------|---------|
| `extract_data.js` | **Browser console script** - Easiest way to extract data |
| `analyze_auctions.py` | **Main analysis script** - Processes auction data |
| `parse_har.py` | HAR file parser (alternative method) |
| `scraper.py` | Cookie-based scraper (backup method) |
| `scraper_selenium.py` | Selenium automation (backup method) |
| `scraper_with_cookies.py` | Selenium with cookie injection (backup method) |
| `BROWSER_CONSOLE_INSTRUCTIONS.md` | Detailed console instructions |
| `SCRAPING_GUIDE.md` | Guide for all extraction methods |

---

## 🔄 Alternative Methods

### Method 2: HAR File Export

If the console script doesn't work:

1. Open Chrome DevTools (`Cmd+Option+I`)
2. Go to **Network** tab
3. Filter by: `api`
4. Reload and navigate through the trading pages
5. Right-click → **Save all as HAR with content**
6. Save as `mpg_network_data.har`
7. Run:
   ```bash
   python3 parse_har.py mpg_network_data.har
   ```

### Method 3: Direct API Scraping

```bash
python3 scraper.py
```

Note: This may not work if MPG's API requires specific authentication.

---

## 📊 What the Analysis Provides

Once you run `analyze_auctions.py`, you'll get:

### Bidder Performance Metrics
- **Total bids placed** - How active each player was
- **Auctions won** - Success count
- **Win rate %** - Efficiency (won/total bids)
- **Total spent** - Budget used
- **Average price paid** - Value efficiency

### Bidding Strategy Analysis
- **Aggressive bidders** - Many bids, high win rate
- **Snipers** - Few bids, high win rate (last-minute bidding)
- **Conservative bidders** - Selective, value-focused
- **Overpayers** - High average prices paid

### Value Analysis
- Who got players for below market value
- Who consistently overpaid
- Best value picks
- Worst value picks

---

## 🛠 Troubleshooting

### "No auction data found"

The console script needs API calls to be captured. Make sure to:
1. Run the script while on the trading page
2. Click around actively during the 10-second capture window
3. Try running it multiple times and combining the data

### "File not found" errors

Make sure to move the downloaded JSON file to the MPG directory:
```bash
mv ~/Downloads/mpg_auction_data.json /Users/baptiste/Desktop/Apps/MPG/
```

### Console script doesn't run

- Make sure you copied the **entire** script from `extract_data.js`
- Check you're in the **Console** tab (not Elements or Network)
- Refresh the page and try again

### Need more help?

See detailed instructions in:
- `BROWSER_CONSOLE_INSTRUCTIONS.md` - Step-by-step console guide
- `SCRAPING_GUIDE.md` - All extraction methods explained

---

## 📦 Dependencies

```bash
pip3 install -r requirements.txt
```

Includes:
- `requests` - HTTP requests
- `browser-cookie3` - Chrome cookie extraction
- `selenium` - Browser automation

---

## 🎯 Next Steps

After extracting data, you can extend the analysis:

1. **Compare to player performance** - Match auction prices to actual points scored
2. **Time analysis** - When are the best deals made?
3. **Visualizations** - Create charts showing bidding patterns
4. **Budget efficiency** - Who used their budget most effectively?

---

## 💡 Tips for Best Results

1. **Navigate extensively** - Click through all auction types while the console script runs
2. **Run multiple times** - Capture data from different views (active, completed, history)
3. **Combine data** - Merge multiple extraction sessions for complete coverage
4. **Check the JSON** - Open the file to see what data was captured before analyzing

---

## 📝 License

For personal use analyzing your own MPG league data.
