#!/usr/bin/env python3
"""
Test AuthService directly without Flask server
"""
import sys
sys.path.insert(0, '.')

from services.auth_service import AuthService
import json

def test_auth_service():
    """Test AuthService methods directly"""
    print("=== Testing AuthService Directly ===")
    
    # Initialize service
    auth_service = AuthService()
    print("✅ AuthService initialized")
    
    # Test user registration
    print("\n1. Testing user registration...")
    signup_result = auth_service.register_user(
        name="Test User",
        email="testuser@example.com",
        password="password123"
    )
    print(f"Signup result: {json.dumps(signup_result, indent=2)}")
    
    if signup_result['success']:
        print("✅ User registration successful!")
        
        # Test authentication
        print("\n2. Testing user authentication...")
        login_result = auth_service.authenticate_user(
            email="testuser@example.com",
            password="password123"
        )
        print(f"Login result: {json.dumps(login_result, indent=2, default=str)}")
        
        if login_result['success']:
            print("✅ User authentication successful!")
            
            session_id = login_result['session_id']
            print(f"Session ID: {session_id}")
            
            # Test session validation
            print("\n3. Testing session validation...")
            user_data = auth_service.validate_session(session_id)
            print(f"Session validation result: {user_data}")
            
            if user_data:
                print("✅ Session validation successful!")
                
                # Test logout
                print("\n4. Testing logout...")
                logout_result = auth_service.logout_user(session_id)
                print(f"Logout result: {logout_result}")
                
                if logout_result:
                    print("✅ Logout successful!")
                    
                    # Test invalid session
                    print("\n5. Testing invalid session...")
                    invalid_user = auth_service.validate_session(session_id)
                    print(f"Invalid session result: {invalid_user}")
                    
                    if not invalid_user:
                        print("✅ Invalid session properly handled!")
                        print("\n🎉 ALL TESTS PASSED!")
                    else:
                        print("❌ Invalid session not handled properly!")
                else:
                    print("❌ Logout failed!")
            else:
                print("❌ Session validation failed!")
        else:
            print("❌ User authentication failed!")
            print(f"Error: {login_result.get('error', 'Unknown error')}")
    else:
        print("❌ User registration failed!")
        print(f"Error: {signup_result.get('error', 'Unknown error')}")

if __name__ == '__main__':
    test_auth_service()