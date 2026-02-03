/**
 * MPG Data Extractor - NO HAR EXPORT NEEDED
 *
 * This captures network data WITHOUT needing to export HAR files
 * Just run this script FIRST, THEN navigate the pages
 *
 * INSTRUCTIONS:
 * 1. Open Console (Cmd+Option+J)
 * 2. Paste this ENTIRE script
 * 3. Press Enter
 * 4. Navigate through MPG pages for 1-2 minutes
 * 5. Come back to Console
 * 6. Type: stopCapture()
 * 7. File downloads automatically
 */

console.clear();
console.log('%c MPG Network Capture Started! ', 'background: #4CAF50; color: white; font-size: 16px; padding: 10px;');
console.log('\n📝 INSTRUCTIONS:');
console.log('   1. Navigate through MPG trading pages');
console.log('   2. Click on auctions, players, mercato backstage');
console.log('   3. When done, type: stopCapture()');
console.log('   4. File will download automatically\n');
console.log('⏱️  Capturing started at:', new Date().toLocaleTimeString());
console.log('━'.repeat(60) + '\n');

// Storage for captured requests
const capturedData = {
    started: new Date().toISOString(),
    requests: []
};

let requestCounter = 0;

// Intercept XMLHttpRequest
const originalXHROpen = XMLHttpRequest.prototype.open;
const originalXHRSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function(method, url) {
    this._captureMethod = method;
    this._captureUrl = url;
    this._captureStartTime = Date.now();
    return originalXHROpen.apply(this, arguments);
};

XMLHttpRequest.prototype.send = function(body) {
    const xhr = this;
    const url = this._captureUrl;
    const method = this._captureMethod;
    const startTime = this._captureStartTime;

    // Only capture MPG API calls
    if (url && (url.includes('api.mpg') || url.includes('mpg.football/api'))) {
        requestCounter++;
        const reqId = requestCounter;

        console.log(`%c[${reqId}] ${method} %c${url.split('?')[0]}`,
            'color: #2196F3; font-weight: bold',
            'color: #666');

        const requestData = {
            id: reqId,
            url: url,
            method: method,
            timestamp: new Date().toISOString(),
            type: 'xhr',
            requestBody: body ? (typeof body === 'string' ? body : '[Binary Data]') : null
        };

        xhr.addEventListener('load', function() {
            const duration = Date.now() - startTime;
            requestData.status = xhr.status;
            requestData.statusText = xhr.statusText;
            requestData.duration = duration;
            requestData.responseSize = xhr.responseText.length;

            // Parse response
            try {
                requestData.response = JSON.parse(xhr.responseText);
                console.log(`%c[${reqId}] ✓ ${xhr.status} %c(${duration}ms, ${(xhr.responseText.length / 1024).toFixed(1)}KB)`,
                    'color: #4CAF50; font-weight: bold',
                    'color: #999; font-size: 11px');
            } catch(e) {
                requestData.responseText = xhr.responseText.substring(0, 1000);
                console.log(`%c[${reqId}] ✓ ${xhr.status} %c(${duration}ms, non-JSON)`,
                    'color: #FF9800; font-weight: bold',
                    'color: #999; font-size: 11px');
            }

            // Get response headers
            requestData.responseHeaders = {};
            const headersString = xhr.getAllResponseHeaders();
            if (headersString) {
                headersString.split('\r\n').forEach(line => {
                    const parts = line.split(': ');
                    if (parts.length === 2) {
                        requestData.responseHeaders[parts[0]] = parts[1];
                    }
                });
            }

            capturedData.requests.push(requestData);
        });

        xhr.addEventListener('error', function() {
            requestData.status = 0;
            requestData.error = 'Network Error';
            capturedData.requests.push(requestData);
            console.log(`%c[${reqId}] ✗ ERROR`, 'color: #F44336; font-weight: bold');
        });
    }

    return originalXHRSend.apply(this, arguments);
};

// Intercept fetch
const originalFetch = window.fetch;

window.fetch = async function(...args) {
    const url = args[0];
    const options = args[1] || {};
    const startTime = Date.now();

    // Only capture MPG API calls
    if (url && (url.includes('api.mpg') || url.includes('mpg.football/api'))) {
        requestCounter++;
        const reqId = requestCounter;
        const method = options.method || 'GET';

        console.log(`%c[${reqId}] ${method} %c${url.split('?')[0]}`,
            'color: #2196F3; font-weight: bold',
            'color: #666');

        const requestData = {
            id: reqId,
            url: url,
            method: method,
            timestamp: new Date().toISOString(),
            type: 'fetch',
            requestBody: options.body || null
        };

        try {
            const response = await originalFetch.apply(this, args);
            const duration = Date.now() - startTime;

            requestData.status = response.status;
            requestData.statusText = response.statusText;
            requestData.duration = duration;

            // Clone and parse response
            const clone = response.clone();

            try {
                const responseData = await clone.json();
                requestData.response = responseData;

                const responseSize = JSON.stringify(responseData).length;
                requestData.responseSize = responseSize;

                console.log(`%c[${reqId}] ✓ ${response.status} %c(${duration}ms, ${(responseSize / 1024).toFixed(1)}KB)`,
                    'color: #4CAF50; font-weight: bold',
                    'color: #999; font-size: 11px');
            } catch(e) {
                try {
                    const text = await clone.text();
                    requestData.responseText = text.substring(0, 1000);
                    requestData.responseSize = text.length;
                    console.log(`%c[${reqId}] ✓ ${response.status} %c(${duration}ms, non-JSON)`,
                        'color: #FF9800; font-weight: bold',
                        'color: #999; font-size: 11px');
                } catch(e2) {
                    console.log(`%c[${reqId}] ✓ ${response.status} %c(${duration}ms)`,
                        'color: #FF9800; font-weight: bold',
                        'color: #999; font-size: 11px');
                }
            }

            capturedData.requests.push(requestData);
            return response;

        } catch(error) {
            requestData.error = error.message;
            capturedData.requests.push(requestData);
            console.log(`%c[${reqId}] ✗ ERROR: ${error.message}`, 'color: #F44336; font-weight: bold');
            throw error;
        }
    }

    return originalFetch.apply(this, args);
};

// Function to stop capture and download
window.stopCapture = function() {
    console.log('\n' + '━'.repeat(60));
    console.log('%c Stopping Capture... ', 'background: #FF9800; color: white; font-size: 14px; padding: 8px;');

    // Restore originals
    window.fetch = originalFetch;
    XMLHttpRequest.prototype.open = originalXHROpen;
    XMLHttpRequest.prototype.send = originalXHRSend;

    capturedData.stopped = new Date().toISOString();
    capturedData.totalRequests = capturedData.requests.length;

    // Show summary
    console.log('\n📊 CAPTURE SUMMARY');
    console.log('━'.repeat(60));
    console.log(`Total Requests: ${capturedData.requests.length}`);
    console.log(`Time Span: ${new Date(capturedData.started).toLocaleTimeString()} - ${new Date(capturedData.stopped).toLocaleTimeString()}`);

    // Group by endpoint
    const endpoints = {};
    capturedData.requests.forEach(req => {
        try {
            const url = new URL(req.url);
            const path = url.pathname;
            endpoints[path] = (endpoints[path] || 0) + 1;
        } catch(e) {}
    });

    console.log('\n📋 Endpoints Captured:');
    Object.entries(endpoints)
        .sort((a, b) => b[1] - a[1])
        .forEach(([path, count]) => {
            console.log(`   ${count}x  ${path}`);
        });

    // Format for analysis
    const outputData = {
        scrape_timestamp: capturedData.stopped,
        url: window.location.href,
        api_calls: capturedData.requests.map(req => ({
            url: req.url,
            method: req.method,
            status: req.status,
            timestamp: req.timestamp,
            response: req.response || req.responseText || null,
            duration_ms: req.duration
        })),
        total_captured: capturedData.requests.length
    };

    // Download
    console.log('\n💾 Downloading data...');

    try {
        const jsonString = JSON.stringify(outputData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mpg_auction_data.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('%c ✓ File Downloaded! ', 'background: #4CAF50; color: white; font-size: 14px; padding: 8px;');
        console.log('\n📁 Check your Downloads folder for: mpg_auction_data.json');
        console.log('\n📊 Next steps:');
        console.log('   1. Move file to: /Users/baptiste/Desktop/Apps/MPG/');
        console.log('   2. Run: python3 analyze_auctions.py mpg_auction_data.json');
        console.log('\n' + '━'.repeat(60) + '\n');

        return outputData;
    } catch(error) {
        console.error('Error creating download:', error);
        console.log('\n⚠️  Download failed, but you can copy the data:');
        console.log(outputData);
        return outputData;
    }
};

// Auto-stop after 10 minutes
setTimeout(() => {
    console.log('\n⏱️  Auto-stopping after 10 minutes...');
    stopCapture();
}, 10 * 60 * 1000);

console.log('🎯 Capture is running!');
console.log('💡 When you\'re done navigating, type: %cstopCapture()', 'color: #4CAF50; font-weight: bold; font-size: 14px');
console.log('');
