#!/usr/bin/env python3
"""
Test login with HTTP request to see debug output
"""
import requests
from time import sleep

def test_login_debug():
    print("🔍 Testing login with debug output...")
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    try:
        # Test login
        print("Attempting login with admin/admin123...")
        
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
        print(f"Login response status: {response.status_code}")
        print(f"Login response headers: {dict(response.headers)}")
        
        if response.status_code == 302:
            print(f"✅ Redirect location: {response.headers.get('Location')}")
            
            # Follow redirect
            dashboard_response = session.get(f"{base_url}/dashboard")
            print(f"Dashboard response status: {dashboard_response.status_code}")
            
            if dashboard_response.status_code == 200:
                print("✅ Dashboard loaded successfully!")
                print(f"Dashboard content length: {len(dashboard_response.text)}")
                if "Dashboard" in dashboard_response.text:
                    print("✅ Dashboard content contains 'Dashboard'")
                else:
                    print("❌ Dashboard content doesn't contain 'Dashboard'")
            else:
                print(f"❌ Dashboard failed with status: {dashboard_response.status_code}")
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"Response content: {response.text[:500]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_login_debug()
