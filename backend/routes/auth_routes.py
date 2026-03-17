"""
Authentication routes for SPARD API
"""
from flask import Blueprint, request, jsonify
import logging
from services import AuthService

logger = logging.getLogger(__name__)

# Create blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize auth service
auth_service = AuthService()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not all([name, email, password]):
            return jsonify({"error": "Name, email, and password are required"}), 400
        
        # Register user
        result = auth_service.register_user(name, email, password)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": "Account created successfully. Please sign in."
            }), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({"error": "Email and password are required"}), 400
        
        # Authenticate user
        result = auth_service.authenticate_user(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    try:
        data = request.get_json()
        session_token = data.get('session_id') if data else None
        
        # Logout user
        auth_service.logout_user(session_token)
        
        return jsonify({
            "success": True,
            "message": "Logout successful"
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify_session():
    """Verify user session endpoint"""
    try:
        data = request.get_json()
        session_token = data.get('session_id') if data else None
        
        if not session_token:
            return jsonify({"error": "Session token required"}), 400
        
        # Validate session
        user = auth_service.validate_session(session_token)
        
        if user:
            return jsonify({
                "success": True,
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email']
                }
            }), 200
        else:
            return jsonify({"error": "Invalid or expired session"}), 401
            
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return jsonify({"error": "Internal server error"}), 500