#!/usr/bin/env python3
"""
Test existing user login
"""
import sys
sys.path.insert(0, '.')

from services.auth_service import AuthService
import json

def test_existing_login():
    """Test login with existing user"""
    print("=== Testing Existing User Login ===")
    
    auth_service = AuthService()
    
    # Test authentication with existing user
    print("Testing user authentication...")
    login_result = auth_service.authenticate_user(
        email="testuser@example.com",
        password="password123"
    )
    print(f"Login result: {json.dumps(login_result, indent=2, default=str)}")
    
    if login_result['success']:
        print("✅ User authentication successful!")
        print(f"User: {login_result['user']['name']} ({login_result['user']['email']})")
        print(f"Session ID: {login_result['session_id']}")
        
        # Test session validation
        session_id = login_result['session_id']
        print(f"\nTesting session validation...")
        user_data = auth_service.validate_session(session_id)
        
        if user_data:
            print("✅ Session validation successful!")
            print(f"Session user: {user_data}")
            print("\n🎉 AUTHENTICATION BACKEND IS WORKING CORRECTLY!")
        else:
            print("❌ Session validation failed!")
    else:
        print("❌ User authentication failed!")
        print(f"Error: {login_result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    test_existing_login()