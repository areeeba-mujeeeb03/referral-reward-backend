import datetime

from main_app.models.admin.error_model import Errors
from main_app.models.admin.help_model import FAQ
from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.utils.user.error_handling import get_error
import logging
from flask import request, jsonify
from main_app.utils.user.string_encoding import generate_encoded_string


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def home_page():
    data = request.get_json()
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()
    try:
        if not user:
            return jsonify({"success" : False, "message" : "User does not exist"})

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if user.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        # validate_session_token(user, access_token, session_id)

        reward = Reward.objects(user_id = user_id).first()
        all_faqs = FAQ.objects(category = "Home Screen FAQs")
        faqs = []
        for faq in all_faqs:
            faq = faq.to_mongo().to_dict()
            faq.pop('_id' , None)
            faq.pop('faq_id', None)
            faq.pop('admin_uid', None)
            faq.pop('category', None)
            faqs.append(faq)


        info = {
            "total_stars": reward.total_stars,
            "total_meteors": reward.total_meteors,
            "galaxy_name": reward.galaxy_name,
            "current_planet": reward.current_planet,
            "invitation_link": user.invitation_link,
            "redeemed_meteors" : reward.redeemed_meteors,
            "faqs" : faqs
        }

        fields_to_encode = ["total_stars", "total_meteors", "galaxy_name", "current_planet", "invitation_link", "redeemed_meteors","faqs"]
        encoded_str = generate_encoded_string(info, fields_to_encode)

        return encoded_str, 200

    except Exception as e:
        Errors(username = user.username, email = user.email,
               error_source = "Sign Up Form", error_type = "server_error").save()
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": "Server error occurred", "success": False}), 500


def my_rewards():
    data = request.get_json()
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()
    try:
        if not user:
            return jsonify({"success" : False, "message" : "User does not exist"})

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if user.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        # validate_session_token(user, access_token, session_id)
        reward = Reward.objects(user_id = user_id).first()
        all_faqs = FAQ.objects(category = "Rewards FAQs")
        faqs = []
        for faq in all_faqs:
            faq = faq.to_mongo().to_dict()
            faq.pop('_id' , None)
            faq.pop('faq_id', None)
            faq.pop('admin_uid', None)
            faq.pop('category', None)
            faqs.append(faq)
        user_reward = Reward.objects(user_id = user_id).first()
        if user :
            info = {
                "invitation_link": user.invitation_link,
                "total_stars": user_reward.total_stars,
                "total_meteors": user_reward.total_meteors,
                # "galaxy_name": list(user_reward.galaxy_name),
                # "current_planet": list(user_reward.current_planet),
                "total_vouchers": user_reward.total_vouchers,
                "invite_code": user.invitation_code,
                "reward_history": list(user_reward.reward_history),
                "faqs" : faqs
            }

            fields_to_encode = ["total_stars",
                                "total_meteors",
                                # "galaxy_name",
                                "total_vouchers",
                                "invite_code",
                                # "current_planet",
                                "reward_history",
                                "invitation_link",
                                "faqs"]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return encoded_str, 200

    except Exception as e:
        Errors(username = user.username, email = user.email,
               error_source = "Sign Up Form", error_type = "server_error").save()
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

def my_referrals():
    data = request.get_json()
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()
    try:
        if not user:
            return jsonify({"success" : False, "message" : "User does not exist"})

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if user.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        # validate_session_token(user, access_token, session_id)
        referral = Referral.objects(user_id = user.user_id).first()
        reward = Reward.objects(user_id = user_id).first()
        all_faqs = FAQ.objects(category = "Referrals FAQs")
        faqs = []
        for faq in all_faqs:
            faq = faq.to_mongo().to_dict()
            faq.pop('_id' , None)
            faq.pop('faq_id', None)
            faq.pop('admin_uid', None)
            faq.pop('category', None)
            faqs.append(faq)

        if user:
            info = {"total_referrals" : referral.total_referrals,
                    "referral_earning": referral.referral_earning,
                    "pending_referrals": referral.pending_referrals,
                    "invitation_link" : user.invitation_link,
                    "all_referrals": referral.all_referrals,
                    "invite_code": user.invitation_code,
                    "faqs" : faqs
            }
            fields_to_encode = ["total_referrals",
                                "referral_earning",
                                "pending_referrals",
                                "all_referrals" ,
                                "invitation_link",
                                "invite_code",
                                "faqs"]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return encoded_str, 200
    except Exception as e:
        Errors(username = user.username, email = user.email,
               error_source = "Sign Up Form", error_type = "server_error").save()
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

#----------------------------------------------------------------------------------------------------

def my_profile():
    data = request.get_json()
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()
    try:
        if not user:
            return jsonify({"success" : False, "message" : "User does not exist"})

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if user.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        reward = Reward.objects(user_id = user_id).first()
        all_faqs = FAQ.objects(category = "Home Screen FAQs")
        faqs = []
        for faq in all_faqs:
            faq = faq.to_mongo().to_dict()
            faq.pop('_id' , None)
            faq.pop('faq_id', None)
            faq.pop('admin_uid', None)
            faq.pop('category', None)
            faqs.append(faq)

        # validate_session_token(user, access_token, session_id)
        if user:
            info = {"username" : user.username,
                    "email" : user.email,
                    "password" : user.password,
                    "mobile_number" : user.mobile_number,
                    "invitation_link" : user.invitation_link,
                    "invite_code" : user.invitation_code,
                    "faqs" : faqs
                    }
            fields_to_encode = ["username",
                                "email",
                                "password"
                                "mobile_number",
                                "invite_link",
                                "invite_code",
                                "faqs"
                                ]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return encoded_str, 200
    except Exception as e:
        Errors(username = user.username, email = user.email,
               error_source = "Sign Up Form", error_type = "server_error").save()
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500