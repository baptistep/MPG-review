# Troubleshooting Guide

## ❌ SecurityError: Failed to read 'toJSON' from 'Window'

**You got this error!** This happens when the page has cross-origin iframes.

### ✅ Solution: Use the Simple Version

I've created a simpler version that avoids this issue:

**Use `extract_data_simple.js` instead of `extract_data.js`**

This version:
- ✅ Only captures network requests (the important data!)
- ✅ Avoids accessing window objects that cause cross-origin errors
- ✅ Gives you 20 seconds instead of 15
- ✅ Shows a countdown timer

### Steps:

1. Open MPG trading page
2. Press `Cmd+Option+J` (Console)
3. Copy **ALL** code from `extract_data_simple.js`
4. Paste and press Enter
5. Click around for 20 seconds (you'll see a countdown)
6. File downloads automatically

---

## 🔍 What If I Still Get Errors?

### Try the HAR File Method Instead

This is 100% reliable and doesn't use JavaScript:

1. Open DevTools (`Cmd+Option+I`)
2. Click **Network** tab
3. Filter by: `api`
4. Navigate through your MPG pages (auctions, players, etc.)
5. Right-click in Network tab → **Save all as HAR with content**
6. Save as `mpg_network_data.har`
7. Run:
   ```bash
   python3 parse_har.py mpg_network_data.har
   ```

---

## 📊 No API Calls Captured?

If you ran the script but got 0 API calls:

### Possible Causes:

1. **You didn't navigate** - You must click around during the capture window
2. **Data already loaded** - The page loaded before you ran the script
3. **Different API structure** - MPG might use a different method

### Solutions:

**Option 1: Run Script BEFORE Page Loads**
```javascript
// In console, while on a different page:
// 1. Paste the script
// 2. Press Enter
// 3. THEN navigate to the trading page
// 4. Click around for the full duration
```

**Option 2: Force Reload During Capture**
```javascript
// 1. Paste the script
// 2. Press Enter
// 3. Immediately press Cmd+R to reload
// 4. Click around aggressively
```

**Option 3: Run Multiple Times**
- Run the script on different sections:
  - Active auctions page
  - Completed auctions page
  - Player details
  - Trading history
- Combine all the downloaded JSON files

---

## 📁 File Not Downloading?

### Check Your Downloads Folder
```bash
ls -lt ~/Downloads | head -20
```

### Browser Blocked the Download?
- Check browser's download bar at bottom
- Check if popup blocker is active
- Try allowing downloads for mpg.football

### Manual Copy Method
If the file won't download, the data is logged to console:

1. Look for the output in the console
2. Right-click on the JSON object → **Copy object**
3. Paste into a text editor
4. Save as `mpg_auction_data.json`

---

## 🔧 Other Issues

### "Unexpected token" or Syntax Error
- Make sure you copied the **ENTIRE** script
- Check you didn't accidentally copy extra characters
- Try copying again from the raw file

### Console Closes or Clears
- The script continues running even if console clears
- Wait for the full duration (15-20 seconds)
- The download will still happen

### Need to Capture More Data
- Increase the timer in the script:
  ```javascript
  // Change this line:
  await new Promise(resolve => setTimeout(resolve, 15000));
  // To longer time (e.g., 30 seconds):
  await new Promise(resolve => setTimeout(resolve, 30000));
  ```

---

## ✅ Verifying Your Data

After extraction, check if you got good data:

```bash
cd /Users/baptiste/Desktop/Apps/MPG

# Check file size
ls -lh mpg_auction_data.json

# Preview the data
head -50 mpg_auction_data.json

# Count API calls
cat mpg_auction_data.json | grep '"url"' | wc -l
```

**Good signs:**
- File is > 5 KB
- You see URLs containing `api.mpg.football`
- You see `response` objects with player/auction data

**Bad signs:**
- File is < 1 KB
- Empty `api_calls` array
- No response data

If you have bad data, try the HAR file method instead.

---

## 🆘 Still Stuck?

Contact info:
1. Check all files in this directory
2. Try each method in order:
   - `extract_data_simple.js` (easiest)
   - `extract_data.js` (more data)
   - HAR file method (most reliable)
3. Read the SCRAPING_GUIDE.md for alternative approaches
