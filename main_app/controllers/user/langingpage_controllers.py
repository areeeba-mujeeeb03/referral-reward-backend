import datetime

from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from flask import jsonify
from main_app.utils.user.error_handling import get_error
import logging
from flask import request, jsonify
from main_app.utils.user.string_encoding import generate_encoded_string
from main_app.controllers.user.auth_controllers import validate_session_token


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def home_page():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id = user_id).first()

        if not user_exist:
            return jsonify({"success" : False, "message" : "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success" :False,
                     "message" : "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success" : False,
                     "message" : "Session mismatch or invalid session"}), 403

        if hasattr(user_exist, 'expiry_time') and user_exist.expiry_time:
            if datetime.datetime.now() > user_exist.expiry_time:
                return ({"success"  : False,
                         "message" : "Access token has expired"}), 401

        # Validate token and session
        # validate_session_token(user_id, access_token, session_id)

        reward = Reward.objects(user_id = user_id).first()

        info = {
            "total_stars": reward.total_stars,
            "total_meteors": reward.total_meteors,
            "galaxy_name": reward.galaxy_name,
            "current_planet": reward.current_planet,
            "invitation_link": user_exist.invitation_link
        }

        fields_to_encode = ["total_stars", "total_meteors", "galaxy_name", "current_planet", "invitation_link"]
        encoded_str = generate_encoded_string(info, fields_to_encode)

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
        user_reward = Reward.objects(user_id = user_id).first()
        if user_exist :
            info = {
                "invitation_link": user_exist.invitation_link,
                "total_stars": user_reward.total_stars,
                "total_meteors": user_reward.total_meteors,
                "galaxy_name": user_reward.galaxy_name,
                "current_planet": user_reward.current_planet,
                "total_vouchers": user_reward.total_vouchers,
                "reward_history": user_reward.reward_history
            }

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
                            })
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

def my_referrals():
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
        referral = Referral.objects(user_id = user_exist.user_id).first()

        if user_exist:
            info = {"total_referrals" : referral.total_referrals,
                    "referral_earning": referral.referral_earning,
                    "pending_referrals": referral.pending_referrals,
                    "all_referrals": referral.all_referrals
            }
            fields_to_encode = ["total_referrals",
                                "referral_earning",
                                "pending_referrals",
                                "all_referrals"
                                ]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return jsonify({"success": True,
                            "earnings": encoded_str
                            })
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

#----------------------------------------------------------------------------------------------------

def my_profile():
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
        if user_exist:
            info = {"username" : user_exist.username,
                    "email" : user_exist.email,
                    "password" : user_exist.password,
                    "mobile_number" : user_exist.mobile_number
                    }
            print(info)
            fields_to_encode = ["username",
                                "email",
                                "password"
                                "mobile_number"
                                ]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return jsonify({"success": True,
                            "earnings": encoded_str
                            })
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500