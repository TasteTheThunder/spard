"""
Authentication service for user management
"""
import bcrypt
import uuid
import logging
from datetime import datetime, timedelta
from models.database import DatabaseManager
from config import Config

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling user authentication and session management"""
    
    def __init__(self):
        """Initialize authentication service"""
        self.db = DatabaseManager()
        logger.info("Authentication service initialized")
    
    def register_user(self, name, email, password):
        """
        Register a new user
        
        Args:
            name (str): User's full name
            email (str): User's email address
            password (str): User's password
            
        Returns:
            dict: Result containing success status and user info
        """
        try:
            # Validate input
            if not all([name, email, password]):
                return {"success": False, "error": "All fields are required"}
            
            # Check if email already exists
            if self.db.get_user_by_email(email.lower().strip()):
                return {"success": False, "error": "Email already registered"}
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user
            user_id = self.db.create_user(name.strip(), email.lower().strip(), password_hash)
            
            if user_id:
                logger.info(f"User registered successfully: {email}")
                return {
                    "success": True, 
                    "message": "User created successfully",
                    "user_id": user_id
                }
            else:
                return {"success": False, "error": "Failed to create user"}
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {"success": False, "error": "Registration failed"}
    
    def authenticate_user(self, email, password):
        """
        Authenticate user login
        
        Args:
            email (str): User's email
            password (str): User's password
            
        Returns:
            dict: Result containing success status and session info
        """
        try:
            # Get user from database
            user = self.db.get_user_by_email(email.lower().strip())
            
            if not user:
                return {"success": False, "error": "Invalid credentials"}
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                return {"success": False, "error": "Invalid credentials"}
            
            # Create session
            session_id = self.create_session(user['id'])
            
            # Update last login
            self.db.update_last_login(user['id'])
            
            # Get user stats
            stats = self.db.get_user_stats(user['id'])
            
            logger.info(f"User authenticated successfully: {email}")
            
            return {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "stats": stats
                },
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {"success": False, "error": "Authentication failed"}
    
    def create_session(self, user_id):
        """
        Create a new session for user
        
        Args:
            user_id (int): User's ID
            
        Returns:
            str: Session token
        """
        try:
            session_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(hours=Config.SESSION_TIMEOUT_HOURS)
            
            self.db.create_session(user_id, session_token, expires_at)
            
            return session_token
            
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            return None
    
    def validate_session(self, session_token):
        """
        Validate session token
        
        Args:
            session_token (str): Session token to validate
            
        Returns:
            dict: User info if valid, None if invalid
        """
        try:
            if not session_token:
                return None
                
            return self.db.validate_session(session_token)
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def logout_user(self, session_token):
        """
        Logout user by invalidating session
        
        Args:
            session_token (str): Session token to invalidate
            
        Returns:
            bool: True if successful
        """
        try:
            if session_token:
                self.db.invalidate_session(session_token)
                logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False