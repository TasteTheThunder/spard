#!/usr/bin/env python3
"""
Test logout functionality
"""
import sys
sys.path.insert(0, '.')

from services.auth_service import AuthService
import json

def test_logout():
    """Test logout functionality"""
    print("=== Testing Logout Functionality ===")
    
    auth_service = AuthService()
    
    # First login to get a session
    print("1. Logging in...")
    login_result = auth_service.authenticate_user(
        email="testuser@example.com",
        password="password123"
    )
    
    if login_result['success']:
        session_id = login_result['session_id']
        print(f"✅ Login successful, session ID: {session_id}")
        
        # Verify session is valid
        print("2. Verifying session is valid...")
        user_data = auth_service.validate_session(session_id)
        if user_data:
            print(f"✅ Session valid for user: {user_data['name']}")
            
            # Test logout
            print("3. Testing logout...")
            logout_result = auth_service.logout_user(session_id)
            if logout_result:
                print("✅ Logout successful")
                
                # Verify session is now invalid
                print("4. Verifying session is now invalid...")
                invalid_user = auth_service.validate_session(session_id)
                if not invalid_user:
                    print("✅ Session properly invalidated")
                    print("\n🎉 LOGOUT FUNCTIONALITY WORKS CORRECTLY!")
                else:
                    print("❌ Session still valid after logout")
            else:
                print("❌ Logout failed")
        else:
            print("❌ Session validation failed")
    else:
        print("❌ Login failed")
        print(f"Error: {login_result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    test_logout()