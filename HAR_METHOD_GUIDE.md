# 📊 HAR File Method - Complete Guide

## Why Use This Method?

✅ **Most Reliable** - Captures ALL network traffic
✅ **No JavaScript Errors** - No cross-origin issues
✅ **Complete Data** - Gets everything the page loads
✅ **Easy to Verify** - You can see exactly what's captured

---

## 🎯 Step-by-Step Instructions

### Step 1: Open DevTools Network Tab

1. Open your MPG trading page in Chrome:
   ```
   https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading
   ```

2. Press `Cmd + Option + I` (or right-click → Inspect)

3. Click the **"Network"** tab at the top

4. In the filter box, type: `api`

### Step 2: Capture Network Traffic

5. Press `Cmd + R` to **reload the page**

6. **Navigate extensively** for 1-2 minutes:
   - ✓ Click "Mercato" or auction tabs
   - ✓ Open player details
   - ✓ View auction history (modal=mercatoBackstage)
   - ✓ Click on different players
   - ✓ Switch between active/completed auctions
   - ✓ Scroll through lists

7. You should see **requests appearing** in the Network tab with URLs like:
   - `api.mpg.football/api/...`
   - Requests with status `200`

### Step 3: Export HAR File

8. **Right-click** anywhere in the Network tab (on the requests list)

9. Select **"Save all as HAR with content"**

10. Save as: `mpg_network_data.har`

11. **Location:** Save to `/Users/baptiste/Desktop/Apps/MPG/`

### Step 4: Run Analysis

12. Open Terminal and run:

```bash
cd /Users/baptiste/Desktop/Apps/MPG
./run_har_analysis.sh
```

**OR manually:**

```bash
cd /Users/baptiste/Desktop/Apps/MPG

# Parse HAR file
python3 parse_har.py mpg_network_data.har

# Analyze auction data
python3 analyze_auctions.py mpg_auction_data.json
```

---

## ✅ How to Verify You Got Good Data

Before closing Chrome DevTools, check:

### In the Network Tab:

- [ ] You see **multiple** requests to `api.mpg.football`
- [ ] Some requests have **large size** (> 10 KB)
- [ ] Click on a request → **Preview** tab shows JSON with player/auction data

### Common API Endpoints You Should See:

```
/api/league/mpg_league_1XQHDZXWT
/api/division/mpg_division_1XQHDZXWT_23_1
/api/championship-players-pool/...
/api/mercato/...
/api/trading/...
```

### After Parsing:

```bash
# Check file size (should be > 5 KB)
ls -lh mpg_auction_data.json

# Count captured API calls (should be > 10)
cat mpg_auction_data.json | grep '"url"' | wc -l
```

---

## 🔍 Troubleshooting

### No API Calls Showing?

**Problem:** Filter might be too strict

**Solution:**
- Clear the filter (delete `api`)
- Look for requests to `mpg.football`
- Or save ALL requests (they'll be filtered during parsing)

### HAR File Too Small?

**Problem:** Not enough navigation

**Solution:**
- Delete the HAR file
- Start over from Step 1
- Navigate MORE extensively
- Keep DevTools open longer

### Can't Find "Save as HAR"?

**Different Chrome Version:**
1. Click the **download icon** (⬇) in the Network tab toolbar
2. Or use the **Export** button
3. Or right-click → **"Copy" → "Copy all as HAR"** → paste into a file

---

## 📊 What Data You'll Get

After successful extraction and analysis, you'll see:

### Player Auction Data:
- Who bid on which players
- Final prices paid
- Auction timestamps
- Winning bidders

### Bidding Patterns:
- Aggressive vs. conservative bidders
- Sniping behavior (last-second bids)
- Budget usage per player

### Performance Metrics:
- Win rates per bidder
- Average prices paid
- Best value acquisitions
- Overpaid vs. underpaid players

---

## 💡 Pro Tips

1. **Navigate BEFORE saving** - The more pages you visit, the more data
2. **Check file size** - HAR file should be > 100 KB for good data
3. **Multiple sessions** - You can combine data from multiple HAR files
4. **Keep DevTools open** - Don't close until after saving

---

## ⏭️ Next Steps

Once you have the `mpg_auction_data.json` file:

1. Run the analysis script
2. Review the bidder performance report
3. Identify auction strategies
4. Optionally: Extend the analysis with custom queries

---

**Need help?** Check `TROUBLESHOOTING.md`
