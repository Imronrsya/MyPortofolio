#!/usr/bin/env python3
"""
Debug script to test login functionality
"""
import sqlite3
from werkzeug.security import check_password_hash

def test_login(username, password):
    print(f"Testing login for username: {username}")
    
    # Connect to database
    conn = sqlite3.connect('finance_manager.db')
    conn.row_factory = sqlite3.Row
    
    # Get user from database
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    
    if user:
        print(f"User found: ID={user['id']}, Username={user['username']}")
        print(f"Password hash: {user['password_hash'][:30]}...")
        
        # Test password verification
        password_valid = check_password_hash(user['password_hash'], password)
        print(f"Password verification result: {password_valid}")
        
        if password_valid:
            print("✅ Login should work!")
            return True
        else:
            print("❌ Password doesn't match")
            return False
    else:
        print("❌ User not found")
        return False

if __name__ == "__main__":
    print("=== Testing login functionality ===")
    
    # Test with known users
    test_login("admin", "admin123")
    print()
    test_login("testuser", "test123")
    print()
    test_login("imronrsya", "imron123")
    print()
    test_login("nonexistent", "wrongpass")
