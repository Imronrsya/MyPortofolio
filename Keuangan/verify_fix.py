#!/usr/bin/env python3
"""
Quick test to verify the template error is fixed
"""
import requests

def test_template_fix():
    base_url = "http://127.0.0.1:5000"
    
    try:
        print("🔍 Testing login page...")
        response = requests.get(f"{base_url}/login")
        
        if response.status_code == 200:
            print("✅ Login page loads successfully!")
            print(f"   Content length: {len(response.text)} characters")
            
            if "TemplateRuntimeError" in response.text:
                print("❌ Still has TemplateRuntimeError")
                return False
            elif "login" in response.text.lower():
                print("✅ Login page content looks good")
                
                # Test login functionality
                print("\n🔍 Testing login with credentials...")
                session = requests.Session()
                
                login_data = {
                    'username': 'admin',
                    'password': 'admin123'
                }
                
                login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=False)
                
                if login_response.status_code == 302:
                    print("✅ Login redirect working!")
                    
                    dashboard_response = session.get(f"{base_url}/dashboard")
                    if dashboard_response.status_code == 200:
                        print("✅ Dashboard accessible!")
                        return True
                    else:
                        print(f"❌ Dashboard failed: {dashboard_response.status_code}")
                        return False
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    return False
            else:
                print("❌ Login page content doesn't look right")
                return False
        else:
            print(f"❌ Login page failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=== Template Fix Verification ===")
    success = test_template_fix()
    
    if success:
        print("\n🎉 TemplateRuntimeError FIXED! Login is working perfectly!")
    else:
        print("\n💥 Still having issues. Check the output above.")
