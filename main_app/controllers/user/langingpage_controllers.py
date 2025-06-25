from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.utils.user.error_handling import get_error
from main_app.controllers.user.auth_controllers import validate_session_token
import logging
from flask import request, jsonify
from main_app.utils.user.string_encoding import generate_encoded_string


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def home_page():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id = user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        reward = Reward.objects(user_id=user.user_id).first()

        if not reward:
            return jsonify({"message": "Reward Not Found", "success": False}), 404
        print("working 1")
        info = {
            "total_stars": reward.total_stars,
            "total_meteors": reward.total_meteors,
            "galaxy_name": reward.galaxy_name,
            "current_planet": reward.current_planet,
            "invitation_link": user.invitation_link
        }

        fields_to_encode = ["total_stars", "total_meteors", "galaxy_name", "current_planet", "invitation_link"]

        encoded_str = generate_encoded_string(info, fields_to_encode)
        print("working 2")
        return jsonify({
            "success": True,
            "encoded_earnings": encoded_str
        }), 200

    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": "Server error occurred", "success": False}), 500


def my_rewards():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id = user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        user_reward = Reward.objects(user_id = user_id).first()
        if user :
            info = {
                "invitation_link": user.invitation_link,
                "total_stars": user_reward.total_stars,
                "total_meteors": user_reward.total_meteors,
                "galaxy_name": user_reward.galaxy_name,
                "current_planet": user_reward.current_planet,
                "total_vouchers": user_reward.total_vouchers,
                "reward_history": user_reward.reward_history
            }
            print("working 1")
            fields_to_encode = ["total_stars",
                                "total_meteors",
                                "galaxy_name",
                                "total_vouchers",
                                "current_planet",
                                "reward_history",
                                "invitation_link"]

            encoded_str = generate_encoded_string(info, fields_to_encode)

            return jsonify({"success" : True,
                            "earnings" : encoded_str
                            }), 200
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

def my_referrals():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id = user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        referral = Referral.objects(user_id = user_id).first()

        if user:
            info = {"total_referrals" : referral.total_referrals,
                    "referral_earning": referral.referral_earning,
                    "pending_referrals": referral.pending_referrals,
                    "all referrals": referral.all_referrals
            }
            fields_to_encode = ["total_referrals",
                                "referral_earnings",
                                "pending_referrals",
                                "all_referrals"]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            print("working 3")
            return jsonify({"success": True,
                            "earnings": encoded_str
                            }), 200
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

#----------------------------------------------------------------------------------------------------

def my_profile():
    try:
        data = request.json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user = User.objects(user_id = user_id).first()

        if not user:
            return jsonify({"message": "User not found", "success": False}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        # Validate token and session first
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)

        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        if user:
            info = {"username" : user.mobile_number,
                    "email" : user.email,
                    "password" : user.password,
                    "mobile_number" : user.mobile_number
                    }

            fields_to_encode = ["username",
                                "email",
                                "password"
                                "mobile_number"
                                ]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return jsonify({"success": True,
                            "earnings": encoded_str

                            }), 200
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500