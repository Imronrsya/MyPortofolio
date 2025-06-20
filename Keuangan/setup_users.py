#!/usr/bin/env python3
"""
Script to create or update user credentials for testing
"""
import sqlite3
from werkzeug.security import generate_password_hash

def create_or_update_user(username, password, email=None):
    conn = sqlite3.connect('finance_manager.db')
    conn.row_factory = sqlite3.Row
    
    # Check if user exists
    existing_user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    
    password_hash = generate_password_hash(password)
    
    if existing_user:
        # Update existing user
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (password_hash, username)
        )
        print(f"✅ Updated password for existing user: {username}")
    else:
        # Create new user
        if email is None:
            email = f"{username}@test.com"
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        print(f"✅ Created new user: {username} with email: {email}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("=== Setting up test users ===")
    
    # Create/update test users with known passwords
    create_or_update_user("admin", "admin123")
    create_or_update_user("testuser", "test123")
    create_or_update_user("imronrsya", "imron123")
    
    print("\n=== Test credentials ===")
    print("Username: admin, Password: admin123")
    print("Username: testuser, Password: test123")
    print("Username: imronrsya, Password: imron123")
