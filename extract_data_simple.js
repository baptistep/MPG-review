/**
 * MPG Auction Data Extractor - SIMPLE VERSION
 *
 * This version ONLY captures network requests and avoids window object access
 * Use this if the main extract_data.js gives cross-origin errors
 *
 * Instructions:
 * 1. Open the MPG trading page
 * 2. Press Cmd+Option+J (Mac) or Ctrl+Shift+J (Windows/Linux)
 * 3. Copy and paste this entire script
 * 4. Press Enter
 * 5. Click around the page for 20 seconds
 * 6. The data will download as mpg_auction_data.json
 */

(async function() {
    console.log('🚀 MPG Data Extractor (Simple Mode)\n');
    console.log('⏰ You have 20 seconds to click around...\n');

    const capturedRequests = [];

    // Intercept XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._mpg_method = method;
        this._mpg_url = url;
        return originalXHROpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        const xhr = this;
        const url = this._mpg_url;
        const method = this._mpg_method;

        if (url && (url.includes('api.mpg') || url.includes('mpg.football'))) {
            console.log(`📡 XHR: ${method} ${url}`);

            const requestInfo = {
                url: url,
                method: method,
                timestamp: new Date().toISOString(),
                type: 'xhr'
            };

            xhr.addEventListener('load', function() {
                requestInfo.status = xhr.status;

                try {
                    const responseData = JSON.parse(xhr.responseText);
                    requestInfo.response = responseData;
                    console.log(`  ✓ Captured: ${url.split('?')[0]}`);
                } catch(e) {
                    requestInfo.response_text = xhr.responseText.substring(0, 500);
                }

                capturedRequests.push(requestInfo);
            });
        }

        return originalXHRSend.apply(this, arguments);
    };

    // Intercept fetch
    const originalFetch = window.fetch;

    window.fetch = async function(...args) {
        const url = args[0];
        const options = args[1] || {};

        const response = await originalFetch.apply(this, args);

        if (url && (url.includes('api.mpg') || url.includes('mpg.football'))) {
            console.log(`📡 Fetch: ${options.method || 'GET'} ${url}`);

            const requestInfo = {
                url: url,
                method: options.method || 'GET',
                timestamp: new Date().toISOString(),
                type: 'fetch',
                status: response.status
            };

            try {
                const clone = response.clone();
                const responseData = await clone.json();
                requestInfo.response = responseData;
                console.log(`  ✓ Captured: ${url.split('?')[0]}`);
            } catch(e) {
                try {
                    const clone = response.clone();
                    const text = await clone.text();
                    requestInfo.response_text = text.substring(0, 500);
                } catch(e2) {
                    // Can't read response
                }
            }

            capturedRequests.push(requestInfo);
        }

        return response;
    };

    // Countdown timer
    for (let i = 20; i > 0; i--) {
        if (i % 5 === 0) {
            console.log(`⏰ ${i} seconds remaining... (${capturedRequests.length} requests captured so far)`);
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    // Restore
    window.fetch = originalFetch;
    XMLHttpRequest.prototype.open = originalXHROpen;
    XMLHttpRequest.prototype.send = originalXHRSend;

    console.log('\n' + '='.repeat(60));
    console.log('CAPTURE COMPLETE');
    console.log('='.repeat(60));
    console.log(`Total API calls captured: ${capturedRequests.length}\n`);

    // Show unique endpoints
    const endpoints = [...new Set(capturedRequests.map(r => {
        try {
            const url = new URL(r.url);
            return url.pathname;
        } catch(e) {
            return r.url.split('?')[0];
        }
    }))];

    console.log('📋 Captured Endpoints:');
    endpoints.forEach(ep => console.log(`  - ${ep}`));

    // Prepare data
    const data = {
        scrape_timestamp: new Date().toISOString(),
        url: window.location.href,
        api_calls: capturedRequests,
        total_captured: capturedRequests.length
    };

    // Download
    console.log('\n💾 Downloading...');

    try {
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mpg_auction_data.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('✅ DONE! File downloaded to your Downloads folder\n');
    } catch(error) {
        console.error('❌ Error:', error);
        console.log('\nYou can copy the data manually:');
        console.log(JSON.stringify(data, null, 2));
    }

    return data;
})();
