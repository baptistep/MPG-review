/**
 * MPG Auction Data Extractor
 *
 * Run this script in your browser console while on the MPG trading page:
 * https://mpg.football/league/.../trading
 *
 * Instructions:
 * 1. Open the MPG trading page
 * 2. Press Cmd+Option+J (Mac) or Ctrl+Shift+J (Windows/Linux) to open Console
 * 3. Copy and paste this entire script
 * 4. Press Enter
 * 5. The data will be downloaded as mpg_auction_data.json
 */

(async function() {
    console.log('🚀 Starting MPG Auction Data Extraction...\n');

    const data = {
        scrape_timestamp: new Date().toISOString(),
        url: window.location.href,
        extracted_data: {}
    };

    // Extract from localStorage
    console.log('📦 Extracting localStorage...');
    data.extracted_data.localStorage = {...localStorage};

    // Extract from sessionStorage
    console.log('📦 Extracting sessionStorage...');
    data.extracted_data.sessionStorage = {...sessionStorage};

    // Try to find global app data
    console.log('🔍 Searching for global data...');
    const globalKeys = Object.keys(window).filter(key =>
        key.toLowerCase().includes('mpg') ||
        key.toLowerCase().includes('store') ||
        key.toLowerCase().includes('state') ||
        key.startsWith('__')
    );

    // Safe serialization helper
    function safeSerialize(obj, maxDepth = 3, currentDepth = 0) {
        if (currentDepth > maxDepth) return '[Max Depth Reached]';
        if (obj === null) return null;
        if (obj === undefined) return undefined;

        const type = typeof obj;
        if (type === 'string' || type === 'number' || type === 'boolean') {
            return obj;
        }

        if (type === 'function') return '[Function]';

        if (Array.isArray(obj)) {
            try {
                return obj.map(item => safeSerialize(item, maxDepth, currentDepth + 1));
            } catch(e) {
                return '[Array - Access Denied]';
            }
        }

        if (type === 'object') {
            const result = {};
            try {
                for (const key in obj) {
                    try {
                        // Skip known problematic properties
                        if (key === 'toJSON' || key.includes('iframe') || key.includes('frame')) {
                            continue;
                        }
                        const value = obj[key];
                        result[key] = safeSerialize(value, maxDepth, currentDepth + 1);
                    } catch(e) {
                        result[key] = '[Access Denied]';
                    }
                }
            } catch(e) {
                return '[Object - Access Denied]';
            }
            return result;
        }

        return '[Unknown Type]';
    }

    globalKeys.forEach(key => {
        try {
            const value = window[key];
            if (value && typeof value === 'object' && !key.includes('frame')) {
                console.log(`  ✓ Found: window.${key}`);
                data.extracted_data[`window_${key}`] = safeSerialize(value);
            }
        } catch(e) {
            console.log(`  ✗ Could not access: window.${key}`);
        }
    });

    // Try to access Redux store if available
    if (window.store) {
        console.log('  ✓ Found Redux store');
        try {
            data.extracted_data.redux_state = safeSerialize(window.store.getState());
        } catch(e) {
            console.log('  ✗ Could not extract Redux state');
        }
    }

    // Try to find React component data
    try {
        const root = document.querySelector('#root') || document.querySelector('[data-reactroot]');
        if (root && root._reactRootContainer) {
            console.log('  ✓ Found React root');
        }
    } catch(e) {}

    // Intercept fetch and XHR requests
    console.log('\n🌐 Setting up network interceptor...');
    console.log('⏰ Please navigate around the page (click on auctions, players, etc.)');
    console.log('   This will capture API calls for 15 seconds...\n');

    const capturedRequests = [];

    // Intercept XMLHttpRequest
    const originalXHROpen = XMLHttpRequest.prototype.open;
    const originalXHRSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function(method, url) {
        this._method = method;
        this._url = url;
        return originalXHROpen.apply(this, arguments);
    };

    XMLHttpRequest.prototype.send = function() {
        const xhr = this;
        const url = this._url;
        const method = this._method;

        console.log(`📡 XHR Call: ${method} ${url}`);

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
                console.log(`  ✓ Captured XHR response from: ${url}`);
            } catch(e) {
                requestInfo.response_type = 'non-json';
                requestInfo.response_preview = xhr.responseText.substring(0, 200);
            }

            capturedRequests.push(requestInfo);
        });

        xhr.addEventListener('error', function() {
            requestInfo.error = 'XHR Error';
            capturedRequests.push(requestInfo);
        });

        return originalXHRSend.apply(this, arguments);
    };

    // Store original fetch
    const originalFetch = window.fetch;

    // Override fetch
    window.fetch = async function(...args) {
        const url = args[0];
        const options = args[1] || {};

        console.log(`📡 API Call: ${url}`);

        const requestInfo = {
            url: url,
            method: options.method || 'GET',
            timestamp: new Date().toISOString(),
            type: 'fetch'
        };

        try {
            const response = await originalFetch.apply(this, args);
            const clone = response.clone();

            requestInfo.status = response.status;

            // Try to get response data
            try {
                const responseData = await clone.json();
                // Use safe serialization for the response
                requestInfo.response = JSON.parse(JSON.stringify(responseData));
                console.log(`  ✓ Captured response from: ${url}`);
            } catch(e) {
                // Not JSON or can't serialize
                try {
                    const text = await clone.text();
                    requestInfo.response_type = 'text';
                    requestInfo.response_preview = text.substring(0, 200);
                } catch(e2) {
                    requestInfo.response_type = 'non-serializable';
                }
            }

            capturedRequests.push(requestInfo);
            return response;
        } catch(error) {
            requestInfo.error = error.message;
            capturedRequests.push(requestInfo);
            throw error;
        }
    };

    // Wait 15 seconds for user to navigate
    await new Promise(resolve => setTimeout(resolve, 15000));

    // Restore original fetch and XHR
    window.fetch = originalFetch;
    XMLHttpRequest.prototype.open = originalXHROpen;
    XMLHttpRequest.prototype.send = originalXHRSend;

    console.log(`\n✅ Captured ${capturedRequests.length} API calls`);
    data.api_calls = capturedRequests;

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('EXTRACTION SUMMARY');
    console.log('='.repeat(60));
    console.log(`Timestamp: ${data.scrape_timestamp}`);
    console.log(`URL: ${data.url}`);
    console.log(`API Calls Captured: ${capturedRequests.length}`);
    console.log(`Local Storage Keys: ${Object.keys(data.extracted_data.localStorage || {}).length}`);
    console.log(`Global Objects Found: ${Object.keys(data.extracted_data).length - 2}`);

    console.log('\n📋 Captured API Endpoints:');
    const uniqueEndpoints = [...new Set(capturedRequests.map(r => {
        try {
            const url = new URL(r.url);
            return url.pathname;
        } catch(e) {
            return r.url;
        }
    }))];
    uniqueEndpoints.forEach(endpoint => console.log(`  - ${endpoint}`));

    // Download as JSON
    console.log('\n💾 Downloading data as JSON...');

    // Custom JSON replacer to handle circular references and problematic objects
    const seen = new WeakSet();
    const jsonReplacer = (key, value) => {
        if (typeof value === 'object' && value !== null) {
            // Skip circular references
            if (seen.has(value)) {
                return '[Circular Reference]';
            }
            seen.add(value);
        }

        // Skip functions, symbols, and undefined
        if (typeof value === 'function') return '[Function]';
        if (typeof value === 'symbol') return '[Symbol]';
        if (value === undefined) return '[Undefined]';

        return value;
    };

    try {
        const jsonString = JSON.stringify(data, jsonReplacer, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mpg_auction_data.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    } catch(error) {
        console.error('Error creating JSON file:', error);
        console.log('Attempting to save with limited data...');

        // Fallback: save just the API calls if the full data fails
        const fallbackData = {
            scrape_timestamp: data.scrape_timestamp,
            url: data.url,
            api_calls: data.api_calls,
            note: 'Some data could not be serialized due to security restrictions'
        };

        const jsonString = JSON.stringify(fallbackData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'mpg_auction_data.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    console.log('\n✅ DONE! Check your Downloads folder for mpg_auction_data.json\n');

    return data;
})();
