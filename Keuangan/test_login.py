#!/usr/bin/env python3
"""
Test script to verify login functionality
"""
import requests
import sqlite3
from werkzeug.security import check_password_hash

def test_database_connection():
    """Test database connection and user existence"""
    try:
        conn = sqlite3.connect('finance_manager.db')
        users = conn.execute('SELECT id, username, email FROM users').fetchall()
        print("✓ Database connection successful")
        print(f"  Users found: {len(users)}")
        for user in users:
            print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_login_endpoint():
    """Test login endpoint with test user"""
    try:
        # Test GET request to login page
        response = requests.get('http://127.0.0.1:5000/login')
        if response.status_code == 200:
            print("✓ Login page accessible")
        else:
            print(f"✗ Login page error: {response.status_code}")
            return False
        
        # Test POST request with credentials
        login_data = {
            'username': 'testuser',
            'password': 'test123'
        }
        
        session = requests.Session()
        response = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        if response.status_code == 200:
            # Check if we're redirected to dashboard or still on login page
            if 'dashboard' in response.url or response.history:
                print("✓ Login successful - redirected to dashboard")
                return True
            else:
                print("✗ Login failed - still on login page")
                return False
        else:
            print(f"✗ Login request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Login test error: {e}")
        return False

def test_dashboard_access():
    """Test dashboard access after login"""
    try:
        session = requests.Session()
        
        # Login first
        login_data = {
            'username': 'testuser', 
            'password': 'test123'
        }
        login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
        
        # Try to access dashboard
        dashboard_response = session.get('http://127.0.0.1:5000/dashboard')
        
        if dashboard_response.status_code == 200 and 'Dashboard' in dashboard_response.text:
            print("✓ Dashboard accessible after login")
            return True
        else:
            print(f"✗ Dashboard access failed: {dashboard_response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Dashboard test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Personal Finance Management Application")
    print("=" * 50)
    
    # Run tests
    db_ok = test_database_connection()
    login_ok = test_login_endpoint()
    dashboard_ok = test_dashboard_access()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Database: {'✓ PASS' if db_ok else '✗ FAIL'}")
    print(f"Login: {'✓ PASS' if login_ok else '✗ FAIL'}")
    print(f"Dashboard: {'✓ PASS' if dashboard_ok else '✗ FAIL'}")
    
    if all([db_ok, login_ok, dashboard_ok]):
        print("\n🎉 All tests passed! Application is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the application.")