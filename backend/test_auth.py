#!/usr/bin/env python3
"""
Test script to verify authentication backend functionality
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_signup():
    """Test user registration"""
    print("Testing user signup...")
    
    signup_data = {
        'name': 'Test User',
        'email': 'testuser@example.com', 
        'password': 'password123'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/auth/signup',
            headers={'Content-Type': 'application/json'},
            json=signup_data
        )
        
        print(f"Signup Response Status: {response.status_code}")
        print(f"Signup Response: {response.json()}")
        
        return response.status_code == 201
        
    except Exception as e:
        print(f"Signup Error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\nTesting user login...")
    
    login_data = {
        'email': 'testuser@example.com',
        'password': 'password123'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            headers={'Content-Type': 'application/json'},
            json=login_data
        )
        
        print(f"Login Response Status: {response.status_code}")
        result = response.json()
        print(f"Login Response: {result}")
        
        if response.status_code == 200 and result.get('success'):
            session_id = result.get('session_id')
            print(f"Login successful! Session ID: {session_id}")
            return session_id
        else:
            return None
            
    except Exception as e:
        print(f"Login Error: {e}")
        return None

def test_verify_session(session_id):
    """Test session verification"""
    print(f"\nTesting session verification...")
    
    verify_data = {
        'session_id': session_id
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/auth/verify',
            headers={'Content-Type': 'application/json'},
            json=verify_data
        )
        
        print(f"Verify Response Status: {response.status_code}")
        print(f"Verify Response: {response.json()}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Verify Error: {e}")
        return False

def check_database():
    """Check if user was created in database"""
    print("\nChecking database...")
    
    try:
        from models.database import DatabaseManager
        db = DatabaseManager()
        user = db.get_user_by_email('testuser@example.com')
        
        if user:
            print(f"User found in database: {user['name']} ({user['email']})")
            return True
        else:
            print("User not found in database")
            return False
            
    except Exception as e:
        print(f"Database check error: {e}")
        return False

if __name__ == '__main__':
    print("=== Authentication Backend Test ===")
    
    # Test signup
    signup_success = test_signup()
    
    if signup_success:
        print("✅ Signup successful!")
        
        # Check database
        db_success = check_database()
        if db_success:
            print("✅ User stored in database!")
        else:
            print("❌ User not found in database!")
        
        # Test login
        session_id = test_login()
        
        if session_id:
            print("✅ Login successful!")
            
            # Test session verification
            verify_success = test_verify_session(session_id)
            
            if verify_success:
                print("✅ Session verification successful!")
                print("\n🎉 All authentication tests passed!")
            else:
                print("❌ Session verification failed!")
        else:
            print("❌ Login failed!")
    else:
        print("❌ Signup failed!")
    
    print("\n=== Test Complete ===")