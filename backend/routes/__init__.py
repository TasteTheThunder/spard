"""
Route blueprints package
"""
from .auth_routes import auth_bp
from .ocr_routes import ocr_bp
from .conflict_routes import conflict_bp

__all__ = ['auth_bp', 'ocr_bp', 'conflict_bp']