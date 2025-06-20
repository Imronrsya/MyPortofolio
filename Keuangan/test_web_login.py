#!/usr/bin/env python3
"""
Test the Flask application login through HTTP requests
"""
import requests
import sys
from time import sleep

def test_flask_login():
    base_url = "http://127.0.0.1:5000"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Check if the app is running
        print("🔍 Testing if Flask app is running...")
        response = session.get(base_url)
        if response.status_code == 200:
            print("✅ Flask app is running!")
        else:
            print(f"❌ Flask app not responding. Status: {response.status_code}")
            return False
        
        # Test 2: Get login page
        print("\n🔍 Testing login page...")
        login_response = session.get(f"{base_url}/login")
        if login_response.status_code == 200 and "login" in login_response.text.lower():
            print("✅ Login page loads successfully!")
        else:
            print(f"❌ Login page failed. Status: {login_response.status_code}")
            return False
        
        # Test 3: Attempt login with test credentials
        print("\n🔍 Testing login with credentials...")
        test_users = [
            ("admin", "admin123"),
            ("testuser", "test123"),
            ("imronrsya", "imron123")
        ]
        
        login_success = False
        for username, password in test_users:
            print(f"   Trying {username}...")
            
            login_data = {
                'username': username,
                'password': password
            }
            
            login_post = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
            
            if login_post.status_code == 302:  # Redirect indicates successful login
                print(f"✅ Login successful for {username}!")
                login_success = True
                
                # Test 4: Access dashboard
                print("\n🔍 Testing dashboard access...")
                dashboard_response = session.get(f"{base_url}/dashboard")
                if dashboard_response.status_code == 200:
                    print("✅ Dashboard accessible after login!")
                else:
                    print(f"❌ Dashboard not accessible. Status: {dashboard_response.status_code}")
                
                # Test 5: Test logout
                print("\n🔍 Testing logout...")
                logout_response = session.get(f"{base_url}/logout")
                if logout_response.status_code == 302:  # Redirect to home
                    print("✅ Logout successful!")
                else:
                    print(f"❌ Logout failed. Status: {logout_response.status_code}")
                
                break
            else:
                print(f"❌ Login failed for {username}. Status: {login_post.status_code}")
        
        if not login_success:
            print("❌ All login attempts failed!")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    print("=== Flask Login Web Test ===")
    print("Make sure Flask app is running on http://127.0.0.1:5000")
    print("Available test credentials:")
    print("- admin / admin123")
    print("- testuser / test123") 
    print("- imronrsya / imron123")
    print("\nStarting tests...\n")
    
    success = test_flask_login()
    
    if success:
        print("\n🎉 All tests passed! Login functionality is working!")
    else:
        print("\n💥 Some tests failed. Check the output above.")
        sys.exit(1)
