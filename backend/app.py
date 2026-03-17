"""
SPARD - Smart Prescription Analysis and Risk Detection
Main Flask application with restructured MVC architecture
"""
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration and routes
from config.settings import Config
from routes import auth_bp, ocr_bp, conflict_bp

def setup_logging():
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/spard.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting SPARD application")
    
    # Load and validate configuration
    try:
        config = Config()
        if not config.validate_config():
            raise Exception("Invalid configuration")
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    # Configure Flask app
    app.secret_key = config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Enable CORS for all routes - allow frontend access
    CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "file://"])
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(ocr_bp)
    app.register_blueprint(conflict_bp)
    
    # Root health check endpoint
    @app.route('/', methods=['GET'])
    def health_check():
        """Main health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "SPARD - Smart Prescription Analysis and Risk Detection",
            "version": "2.0.0",
            "features": [
                "Gemini AI OCR",
                "Drug Conflict Analysis", 
                "User Authentication",
                "Session Management"
            ],
            "database": "SQLite connected",
            "environment": config.FLASK_ENV
        }), 200
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Endpoint not found",
            "message": "The requested resource does not exist"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal server error",
            "message": "Something went wrong on our end"
        }), 500
    
    @app.errorhandler(413)
    def file_too_large(error):
        return jsonify({
            "error": "File too large",
            "message": "Maximum file size is 16MB"
        }), 413
    
    logger.info("SPARD application created successfully")
    return app

# Create the application
app = create_app()

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    
    # Load configuration for development server
    config = Config()
    
    logger.info("Starting SPARD development server")
    logger.info(f"Environment: {config.FLASK_ENV}")
    logger.info(f"Debug mode: {config.DEBUG}")
    
    # Run the development server
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )