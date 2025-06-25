import datetime
import logging
from flask import request, jsonify, session
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token

# ================

# Configuration and setup

# ===============

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from urllib.parse import quote_plus
def generate_msg(user):
    msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
            f"Join using my invite and enjoy exclusive offers on their products. "
            f"Use my invitation link: {user.invitation_link}. Or you can use my invitation code: {user.invitation_code}")
    encoded_msg = quote_plus(msg)
    return encoded_msg

def send_whatsapp_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id=user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        if not user or not user.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user)
        whatsapp_link = f"https://wa.me/?text={encoded_msg}"

        return jsonify({
            "success": True,
            "whatsapp_msg": whatsapp_link
        })

    except Exception as e:
        logger.error(f"WhatsApp invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500


def send_twitter_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id=user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        if not user or not user.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user)
        twitter_link = f"https://twitter.com/intent/tweet?text={encoded_msg}"

        return jsonify({
            "success": True,
            "twitter_link": twitter_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500


def send_telegram_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id=user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        if not user or not user.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user)
        telegram_link = f"https://t.me/share/url?url={quote_plus(user.invitation_link)}&text={encoded_msg}"

        return jsonify({
            "success": True,
            "twitter_link": telegram_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500

def send_facebook_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id=user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        if not user or not user.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        facebook_link = f"https://www.facebook.com/sharer/sharer.php?u={quote_plus(user.invitation_link)}"

        return jsonify({
            "success": True,
            "twitter_link": facebook_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500