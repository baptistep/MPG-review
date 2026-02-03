/**
 * MPG Data Extractor - WITH PAGE RELOAD
 *
 * This version starts intercepting BEFORE the page loads
 * Run this on ANY mpg.football page, then it will reload to the trading page
 */

(async function() {
    console.log('🚀 MPG Data Extractor - Reload Version\n');

    const capturedRequests = [];
    let isCapturing = true;

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

        if (isCapturing && url && url.includes('mpg')) {
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

        if (isCapturing && url && url.includes('mpg')) {
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
                // Not JSON
            }

            capturedRequests.push(requestInfo);
        }

        return response;
    };

    // Check if we're on the trading page
    const targetUrl = 'https://mpg.football/league/mpg_league_1XQHDZXWT/mpg_division_1XQHDZXWT_23_1/trading?modal=mercatoBackstage&initialDivisionId=mpg_division_1XQHDZXWT_23_1';

    if (!window.location.href.includes('trading')) {
        console.log('🔄 Redirecting to trading page...');
        console.log('⏰ Capturing will start automatically!\n');
        window.location.href = targetUrl;

        // Wait for navigation
        await new Promise(resolve => setTimeout(resolve, 30000));
    } else {
        console.log('✓ Already on trading page');
        console.log('🔄 Reloading to capture initial requests...\n');

        // Reload to capture
        window.location.reload();

        // Wait for reload and navigation
        await new Promise(resolve => setTimeout(resolve, 30000));
    }

    // Give time for user interaction
    console.log('⏰ NOW: Click around the page!');
    console.log('   - Click on players');
    console.log('   - Open auction details');
    console.log('   - View mercato backstage\n');

    for (let i = 30; i > 0; i--) {
        if (i % 5 === 0) {
            console.log(`⏰ ${i} seconds... (${capturedRequests.length} captured)`);
        }
        await new Promise(resolve => setTimeout(resolve, 1000));
    }

    isCapturing = false;

    // Restore
    window.fetch = originalFetch;
    XMLHttpRequest.prototype.open = originalXHROpen;
    XMLHttpRequest.prototype.send = originalXHRSend;

    console.log('\n' + '='.repeat(60));
    console.log(`✅ DONE! Captured ${capturedRequests.length} requests`);
    console.log('='.repeat(60) + '\n');

    // Show endpoints
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

    console.log('✅ File downloaded!\n');

    return data;
})();
