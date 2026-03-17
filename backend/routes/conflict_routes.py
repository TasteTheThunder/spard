"""
Conflict analysis routes for SPARD API
"""
from flask import Blueprint, request, jsonify
import logging
from services import ConflictAnalysisService, AuthService

logger = logging.getLogger(__name__)

conflict_bp = Blueprint('conflict', __name__, url_prefix='/api')

conflict_service = ConflictAnalysisService()
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


@conflict_bp.route('/check-multi-prescription-conflicts', methods=['POST'])
@require_auth
def check_multi():
    """Analyze conflicts between two prescription medicine lists"""
    try:
        data = request.get_json()

        doctor_a = data.get("doctor_a_medicines", [])
        doctor_b = data.get("doctor_b_medicines", [])
        user_allergies = data.get("user_allergies", [])

        if not doctor_a and not doctor_b:
            return jsonify({"error": "No medicines provided"}), 400

        result = conflict_service.analyze_multi_prescription_conflicts(
            doctor_a_medicines=doctor_a,
            doctor_b_medicines=doctor_b,
            user_allergies=user_allergies
        )

        return jsonify({
            "success": True,
            "analysis": result,
            "message": "Conflict analysis completed using Gemini AI"
        }), 200

    except Exception as e:
        logger.error(f"Conflict analysis error: {e}")
        return jsonify({"success": False, "error": "Internal error"}), 500
