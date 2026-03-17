"""
OCR routes for SPARD API
"""
from flask import Blueprint, request, jsonify
import logging
import base64
from services import GeminiOCRService, AuthService

logger = logging.getLogger(__name__)

ocr_bp = Blueprint('ocr', __name__, url_prefix='/api')

gemini_service = GeminiOCRService()
auth_service = AuthService()


def require_auth(f):
    def decorated_function(*args, **kwargs):
        session_token = request.headers.get('X-Session-Token')

        if not session_token:
            return jsonify({"error": "Authentication required"}), 401

        user = auth_service.validate_session(session_token)
        if not user:
            return jsonify({"error": "Invalid or expired session"}), 401

        request.user = user
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@ocr_bp.route('/ocr', methods=['POST'])
@require_auth
def process_ocr():
    """Extract medicines directly from prescription image using Gemini OCR"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400

        if not file.content_type.startswith('image/'):
            return jsonify({"error": "Invalid file type"}), 400

        img_bytes = file.read()

        if not img_bytes:
            return jsonify({"error": "Empty image file"}), 400

        # Convert to base64
        base64_image = base64.b64encode(img_bytes).decode('utf-8')

        # Extract medicines using Gemini
        medicines = gemini_service.extract_medicines_from_image(base64_image, doctor="A")

        logger.info(f"OCR medicines extracted: {medicines}")

        return jsonify({
            "success": True,
            "method": "gemini",
            "medicines": medicines,
            "message": "Medicines extracted successfully"
        }), 200

    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        return jsonify({"success": False, "error": "Internal OCR error"}), 500
