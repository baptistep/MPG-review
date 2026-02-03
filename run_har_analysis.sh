#!/bin/bash

echo "==================================="
echo "MPG HAR File Analyzer"
echo "==================================="
echo ""

HAR_FILE="/Users/baptiste/Desktop/Apps/MPG/mpg_network_data.har"

if [ ! -f "$HAR_FILE" ]; then
    echo "❌ HAR file not found: $HAR_FILE"
    echo ""
    echo "Please:"
    echo "1. Open Chrome DevTools (Cmd+Option+I)"
    echo "2. Go to Network tab"
    echo "3. Filter by 'api'"
    echo "4. Navigate through MPG trading pages"
    echo "5. Right-click → 'Save all as HAR with content'"
    echo "6. Save as: mpg_network_data.har"
    echo ""
    exit 1
fi

echo "✓ Found HAR file"
echo ""
echo "Parsing HAR file..."
python3 /Users/baptiste/Desktop/Apps/MPG/parse_har.py "$HAR_FILE"

echo ""
echo "Analyzing auction data..."
python3 /Users/baptiste/Desktop/Apps/MPG/analyze_auctions.py /Users/baptiste/Desktop/Apps/MPG/mpg_auction_data.json

echo ""
echo "✅ Analysis complete!"
