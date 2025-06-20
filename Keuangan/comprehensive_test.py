#!/usr/bin/env python3
"""
Comprehensive test script for Personal Finance Management Application
"""
import requests
import json
from datetime import datetime, date

class FinanceAppTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, passed, message=""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"      {message}")
    
    def login(self, username="testuser", password="test123"):
        """Login to the application"""
        try:
            response = self.session.post(f"{self.base_url}/login", data={
                'username': username,
                'password': password
            })
            success = response.status_code == 200 and (
                'dashboard' in response.url or 
                len(response.history) > 0
            )
            self.log_test("User Login", success, 
                         f"Status: {response.status_code}, URL: {response.url}")
            return success
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False
    
    def test_dashboard(self):
        """Test dashboard access and content"""
        try:
            response = self.session.get(f"{self.base_url}/dashboard")
            success = response.status_code == 200 and "Dashboard" in response.text
            self.log_test("Dashboard Access", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Dashboard Access", False, str(e))
            return False
    
    def test_transactions_page(self):
        """Test transactions page access"""
        try:
            response = self.session.get(f"{self.base_url}/transactions")
            success = response.status_code == 200 and "Transaksi" in response.text
            self.log_test("Transactions Page", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Transactions Page", False, str(e))
            return False
    
    def test_add_transaction(self):
        """Test adding a new transaction"""
        try:
            transaction_data = {
                'category_id': 1,
                'amount': 50000,
                'description': 'Test transaction',
                'date': date.today().isoformat()
            }
            response = self.session.post(f"{self.base_url}/add_transaction", 
                                       data=transaction_data)
            success = response.status_code in [200, 302]  # 302 for redirect
            self.log_test("Add Transaction", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Add Transaction", False, str(e))
            return False
    
    def test_budgets_page(self):
        """Test budgets page access"""
        try:
            response = self.session.get(f"{self.base_url}/budgets")
            success = response.status_code == 200 and "Budget" in response.text
            self.log_test("Budgets Page", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Budgets Page", False, str(e))
            return False
    
    def test_goals_page(self):
        """Test goals page access"""
        try:
            response = self.session.get(f"{self.base_url}/goals")
            success = response.status_code == 200 and ("Goal" in response.text or "Tujuan" in response.text)
            self.log_test("Goals Page", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Goals Page", False, str(e))
            return False
    
    def test_reports_page(self):
        """Test reports page access"""
        try:
            response = self.session.get(f"{self.base_url}/reports")
            success = response.status_code == 200 and ("Report" in response.text or "Laporan" in response.text)
            self.log_test("Reports Page", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Reports Page", False, str(e))
            return False
    
    def test_profile_page(self):
        """Test profile page access"""
        try:
            response = self.session.get(f"{self.base_url}/profile")
            success = response.status_code == 200 and ("Profile" in response.text or "Profil" in response.text)
            self.log_test("Profile Page", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Profile Page", False, str(e))
            return False
    
    def test_logout(self):
        """Test logout functionality"""
        try:
            response = self.session.get(f"{self.base_url}/logout")
            success = response.status_code in [200, 302]
            self.log_test("User Logout", success, 
                         f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("User Logout", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Comprehensive Finance App Tests")
        print("=" * 60)
        
        # Test login first
        if not self.login():
            print("\n❌ Login failed - cannot continue with other tests")
            return False
        
        # Run all functionality tests
        tests = [
            self.test_dashboard,
            self.test_transactions_page,
            self.test_add_transaction,
            self.test_budgets_page,
            self.test_goals_page,
            self.test_reports_page,
            self.test_profile_page,
            self.test_logout
        ]
        
        for test in tests:
            test()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        passed = sum(1 for result in self.test_results if result['passed'])
        total = len(self.test_results)
        
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! Application is fully functional.")
        else:
            print(f"\n⚠️  {total-passed} tests failed. Check the application.")
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = FinanceAppTester()
    tester.run_all_tests()
