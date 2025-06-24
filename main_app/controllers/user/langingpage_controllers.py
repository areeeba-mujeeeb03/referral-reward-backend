from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from flask import jsonify
from main_app.utils.user.error_handling import get_error
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

        if not user_id:
            return jsonify({"message": "Unauthorized User", "success": False}), 401

        user = User.objects(user_id=user_id).first()
        reward = Reward.objects(user_id=user_id).first()

        if not user or not reward:
            return jsonify({"message": "User or Reward Not Found", "success": False}), 404

        info = {
            "total_stars": reward.total_stars,
            "total_meteors": reward.total_meteors,
            "galaxy_name": reward.galaxy_name,
            "current_planet": reward.current_planet,
            "invitation_link": user.invitation_link
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
        user = User.objects(user_id = user_id).first()
        user_reward = Reward.objects(user_id = user_id).first()
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
        if user :
            info = {
                "invitation_link": User.invitation_link,
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
        user  = User.objects(user_id = user_id).first()
        referral = Referral.objects(user_id = user_id).first()
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
        if user:
            info = {"total_referrals" : referral.total_referrals,
                    "referral_earning": referral.referral_earning,
                    "pending_referrals": referral.pending_referrals,
                    "all referrals": referral.all_referrals
            }
            fields_to_encode = ["total_referrals",
                                "referral_earnings",
                                "pending_referrals",
                                "all_referrals",
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
        data = request.json()
        user_id = data.get("user_id")
        user = User.objects(user_id = user_id).first()
 
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
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

                            })
    except Exception as e:
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500