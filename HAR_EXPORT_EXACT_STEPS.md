# How to Export HAR File - Exact Steps

## Method 1: Export Button (Easiest)

1. Open Chrome DevTools (`Cmd+Option+I`)
2. Click **"Network"** tab
3. Look at the **top toolbar** of the Network tab
4. Find the **download icon (⬇️)** or **export icon**
5. Click it → Should say "Export HAR..."
6. Save as `mpg_network_data.har`

**Location of icon:** Top-left area of Network tab, near the filter box

---

## Method 2: Right-Click Method

1. In Network tab
2. Make sure you have **some requests** showing (reload the page if empty)
3. **Right-click on ANY request** in the list (not in empty space)
4. Look for one of these options:
   - "Save all as HAR with content"
   - "Save as HAR with content"
   - "Copy all as HAR"
5. If you see "Copy all as HAR":
   - Select it
   - Open TextEdit
   - Paste (`Cmd+V`)
   - Save as `mpg_network_data.har`

---

## Method 3: Gear Icon Settings

1. In Network tab
2. Click the **⚙️ gear icon** (top-right of Network panel)
3. Check if there's an export option there
4. Or look for "Preserve log" - make sure it's checked

---

## Method 4: Use JavaScript to Extract (Automated)

If you still can't find the HAR export, use this JavaScript method instead:

Copy this entire script and run in Console:
