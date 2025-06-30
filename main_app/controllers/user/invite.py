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
            f"Join using my invite and enjoy exclusive offers on their products. \n\n"
            f"Use my invitation link : {user.invitation_link}.\n"
           f" Or you can use my invitation code: {user.invitation_code}")
    encoded_msg = quote_plus(msg)

    return encoded_msg

def send_whatsapp_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user_exist)
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

        user_exist = User.objects(user_id=user_id).first()


        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user_exist)
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

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user_exist)
        telegram_link = f"https://t.me/share/url?url={quote_plus(user_exist.invitation_link)}&text={encoded_msg}"

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

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        encoded_msg = generate_msg(user_exist)

        facebook_link = f"https://www.facebook.com/sharer/sharer.php?u={quote_plus(user_exist.invitation_link)}"

        return jsonify({
            "success": True,
            "twitter_link": facebook_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500