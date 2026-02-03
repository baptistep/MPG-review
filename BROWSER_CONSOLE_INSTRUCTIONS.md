# Browser Console Data Extraction - Step by Step

This is the **easiest and most reliable** method to extract your MPG auction data.

## Steps:

### 1. Open Your MPG League Page

Navigate to your league's trading page in Chrome:
```
https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading
```

Make sure you're logged in and can see the auction/trading data.

### 2. Open Chrome Developer Console

**Mac:** Press `Cmd + Option + J`
**Windows/Linux:** Press `Ctrl + Shift + J`

You should see a panel appear at the bottom or side of your browser with a `>` prompt.

### 3. Copy the JavaScript Code

Open the file `extract_data.js` in this folder and copy ALL the code (Cmd+A, then Cmd+C).

### 4. Paste and Run

- Click in the console where you see the `>` prompt
- Paste the code (Cmd+V)
- Press `Enter`

### 5. Navigate the Page

**IMPORTANT:** The script will wait for 10 seconds while you navigate around:
- Click on different players in the auction
- Open the auction history modal
- Navigate through tabs (active auctions, completed auctions, etc.)
- The more you click around, the more API calls it will capture!

### 6. Download the Data

After 10 seconds, the script will automatically:
- Download a file called `mpg_auction_data.json` to your Downloads folder
- Show a summary of what was captured in the console

### 7. Move the File

Move `mpg_auction_data.json` from your Downloads folder to:
```
/Users/baptiste/Desktop/Apps/MPG/
```

### 8. Run the Analysis

Once the file is in place, run:
```bash
cd /Users/baptiste/Desktop/Apps/MPG
python3 analyze_auctions.py mpg_auction_data.json
```

---

## What the Script Does

The script captures:
- ✅ All API calls made by the page (including auction data)
- ✅ Response data from those API calls
- ✅ localStorage and sessionStorage data
- ✅ Global application state (Redux, etc.)

## Troubleshooting

**Nothing happens when I paste:**
- Make sure you copied the ENTIRE script from extract_data.js
- Check that you're in the Console tab (not Elements or Network)

**No file downloads:**
- Check your browser's download settings
- Look in your default Downloads folder
- Check if popup blockers are interfering

**Not enough data captured:**
- Run the script again and click around MORE during the 10-second window
- Visit different sections of the trading page

**Still having issues:**
- Try the HAR file method instead (see SCRAPING_GUIDE.md)
