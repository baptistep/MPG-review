# ⚡ Quick Start - 3 Simple Steps

## ⚠️ Got a SecurityError?

**Use `extract_data_simple.js` instead** - It avoids cross-origin issues!

See `TROUBLESHOOTING.md` for details.

---

## Step 1: Open Console (30 seconds)

1. Go to: https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading
2. Press `Cmd + Option + J` (Mac) or `Ctrl + Shift + J` (Windows)
3. Open `extract_data_simple.js`, copy all the code
4. Paste into console, press Enter

## Step 2: Navigate (20 seconds)

While the script runs (you'll see a countdown), click around:
- ✓ Click on different players/auctions
- ✓ Open auction history/mercato backstage
- ✓ Switch between tabs (active/completed)
- ✓ View player details
- ✓ The more you click, the more data!

## Step 3: Analyze

```bash
# Move the downloaded file
mv ~/Downloads/mpg_auction_data.json /Users/baptiste/Desktop/Apps/MPG/

# Run analysis
cd /Users/baptiste/Desktop/Apps/MPG
python3 analyze_auctions.py mpg_auction_data.json
```

---

## 📊 What You'll Get

- Win rates for each bidder
- Total spending per player
- Value efficiency (who got the best deals)
- Bidding strategy insights
- Performance rankings

---

## ❓ Problems?

- **No data captured?** → Click around MORE during the 10-second window
- **File not found?** → Check Downloads folder, move to MPG directory
- **Script won't paste?** → Make sure you're in Console tab, not Elements

Full docs: `README.md` | Detailed instructions: `BROWSER_CONSOLE_INSTRUCTIONS.md`
