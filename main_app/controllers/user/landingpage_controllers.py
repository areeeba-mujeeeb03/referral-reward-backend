import datetime
from main_app.controllers.admin.help_request_controllers import get_faqs_by_category_name
from main_app.controllers.user.rewards_controllers import update_planet_and_galaxy
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.error_model import Errors
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.admin.how_it_work_model import HowItWork
from main_app.models.admin.links import ReferralReward
from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.utils.user.error_handling import get_error
import logging
from flask import request, jsonify
from main_app.utils.user.string_encoding import generate_encoded_string
from main_app.models.admin.product_model import Product
from main_app.models.admin.prize_model import PrizeDetail, AdminPrizes
from main_app.models.admin.advertisment_card_model import AdvertisementCardItem, AdminAdvertisementCard


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
            return jsonify({"success" : False,
                            "message" : "User does not exist"})

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
                         "message": "Access token has expired",
                            "token"  : "expired"}), 401

        # validate_session_token(user, access_token, session_id)
        update_planet_and_galaxy(user_id)
        reward = Reward.objects(user_id = user_id).first()

        info = {
            "total_stars": reward.total_stars,
            "total_meteors": reward.current_meteors,
            "galaxy_name": reward.galaxy_name,
            "current_planet": reward.current_planet,
            "invitation_link": user.invitation_link,
            "redeemed_meteors" : reward.redeemed_meteors,
        }

        fields_to_encode = ["total_stars", "total_meteors", "galaxy_name", "current_planet", "invitation_link", "redeemed_meteors",]
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

    print(user)
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
                         "message": "Access token has expired",
                            "token"  : "expired"}), 401

        # validate_session_token(user, access_token, session_id)
        reward = Reward.objects(user_id = user_id).first()
        admin_uid = user.admin_uid
        update_planet_and_galaxy(user_id)

        user_reward = Reward.objects(user_id = user_id).first()
        if user :
            info = {
                "invitation_link": user.invitation_link,
                "total_stars": user_reward.total_stars,
                "total_meteors": user_reward.current_meteors,
                "total_vouchers": user_reward.total_vouchers,
                "invite_code": user.invitation_code,
                "reward_history": list(user_reward.reward_history),
                 "redeemed_meteors" : reward.redeemed_meteors,
                "redeemed_vouchers": reward.used_vouchers,
                "total_meteors_earned": reward.total_meteors_earned

            }

            fields_to_encode = ["total_stars",
                                "total_meteors",
                                "total_vouchers",
                                "invite_code",
                                "reward_history",
                                "invitation_link",
                                "redeemed_meteors",
                                "redeemed_vouchers"
                                "total_meteors_earned",
                                ]

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
                         "message": "Access token has expired",
                            "token"  : "expired"}), 401

        # validate_session_token(user, access_token, session_id)
        update_planet_and_galaxy(user_id)
        referral = Referral.objects(user_id = user.user_id).first()
        reward = Reward.objects(user_id = user_id).first()

        if user:
            info = {"total_referrals" : referral.total_referrals,
                    "referral_earning": referral.referral_earning,
                    "pending_referrals": referral.pending_referrals,
                    "invitation_link" : user.invitation_link,
                    "all_referrals": referral.all_referrals,
                    "invite_code": user.invitation_code
            }
            fields_to_encode = ["total_referrals",
                                "referral_earning",
                                "pending_referrals",
                                "all_referrals" ,
                                "invitation_link",
                                "invite_code"
                                ]


            encoded_str = generate_encoded_string(info, fields_to_encode)
            return encoded_str, 200
    except Exception as e:
        Errors(username = user.username, email = user.email,
               error_source = "Sign Up Form", error_type = "server_error").save()
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500

##--------------------------------------------PROFILE API-------------------------------------------------------##

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
                         "message": "Access token has expired",
                            "token"  : "expired"}), 401

        update_planet_and_galaxy(user_id)

        reward = Reward.objects(user_id = user_id).first()
        referral = Referral.objects(user_id = user.user_id).first()

        # validate_session_token(user, access_token, session_id)
        if user:
            info = {"username" : user.username,
                    "email" : user.email,
                    "mobile_number" : user.mobile_number,
                    "current_meteors" : reward.current_meteors,
                    "referral_earnings" : referral.referral_earning,
                    "redeemed_meteors" : reward.redeemed_meteors,
                    "invitation_link" : user.invitation_link,
                    "invite_code" : user.invitation_code,
                    "total_meteors_earned" : reward.total_meteors_earned
                    }

            fields_to_encode = ["username",
                                "email",
                                "mobile_number",
                                "current_meteors",
                                "referral_earnings",
                                "redeemed_meteors",
                                "invitation_link",
                                "invite_code",
                                "total_meteors_earned"
                                ]

            encoded_str = generate_encoded_string(info, fields_to_encode)
            return encoded_str, 200

    except Exception as e:
        Errors(username = user.username, email = user.email,
               error_source = "Sign Up Form", error_type = "server_error").save()
        logger.error(f"Server Error: {str(e)}")
        return jsonify({"error": get_error("server_error")}), 500


# -------------------------------------------------------------------------

def fetch_data_from_admin():
    data = request.get_json()
    user_id = data.get("user_id")
    user = User.objects(user_id = user_id).first()
    admin = Admin.objects(admin_uid = user.admin_uid).first()


    if not user:
        return jsonify({"success": False, "message" : "User does not exist"})

    admin_uid = user.admin_uid
    home_faqs = get_faqs_by_category_name(admin_uid, "Home Screen") or []
    rewards_faqs = get_faqs_by_category_name(admin_uid, "Rewards") or []
    referrals_faqs = get_faqs_by_category_name(admin_uid, "Referrals") or []
    help_faqs = get_faqs_by_category_name(admin_uid, "Help and Support FAQs") or []

    how_it_works_text = HowItWork.objects(admin_uid=admin_uid).first()
    update_planet_and_galaxy(user_id)

    if not how_it_works_text:
        return ({"message": "No 'how it works' data found", "success": False}), 404

    how_text = how_it_works_text.to_mongo().to_dict()
    data =[]
    how_text.pop('_id', None)
    how_text.pop('admin_uid', None)
    data.append(how_text)

    prize = AdminPrizes.objects(admin_uid=admin_uid).first()
    prize_data = []

    if prize:
        prize_dict = prize.to_mongo().to_dict()
        prize_dict.pop('_id', None)
        prize_dict.pop('admin_uid', None)
        prize_dict.pop('created_at', None)
        prize_data.append(prize_dict)

    reward = Reward.objects(user_id=user_id).first()
    if not reward or not reward.galaxy_name:
        return jsonify({"message": "User has no galaxy assigned yet"}), 404

    current_galaxy_name = reward.galaxy_name[-1]
    galaxy = Galaxy.objects(galaxy_name=current_galaxy_name).first()

    if not galaxy:
        return jsonify({"message": "Current galaxy not found"}), 404

    galaxy_data = {
        "galaxy_name": galaxy.galaxy_name,
        "total_meteors_required_in_this_galaxy": galaxy.total_meteors_required,
        "total_milestones": galaxy.total_milestones,
        "milestones": []
    }

    for m in galaxy.all_milestones:
        milestones = {
            "milestone_id": m.milestone_id,
            "milestone_name": m.milestone_name,
            "milestone_reward": m.milestone_reward,
            "meteors_required_to_unlock": m.meteors_required_to_unlock,
            "milestone_description": m.milestone_description
        }
        galaxy_data["milestones"].append(milestones)


      # --- Fetch advertisement cards
    ad_data = []
    ad_record = AdminAdvertisementCard.objects(admin_uid=admin_uid).first()
    if ad_record:
        for ad in ad_record.advertisement_cards:
            ad_dict = {
                "title": ad.title,
                "description": ad.description,
                "button_txt": ad.button_txt,
                "image_url": ad.image_url
            }
            ad_data.append(ad_dict)

    conversion_rate = []
    rates = ReferralReward.objects(admin_uid = admin_uid).first()
    conversion_data = {
        "conversion_rates" : rates.conversion_rates,
        "referrer_reward" : rates.referrer_reward,
        "invitee_reward" : rates.invitee_reward,
    }
    conversion_rate.append(conversion_data)


      # --- Merge both
    exclusive_perks = {}
    product_offers = Product.objects(admin_uid = admin_uid)

    # for product in product_offers:
    #     all =
    #     return
    product_data =[]
    # for product in users:
    #     user = user.to_mongo().to_dict()
    #     userdata = {}
    #     userdata['username'] = user['username']
    #     userdata['email'] = user['email']
    #     userdata['mobile_number'] = user['mobile_number']
    #     # product_uid = Product.get('product_uid')  # Ensure this exists in the user model
    #     # # if product_uid:
    #     # product = Product.objects(uid= uid['uid']).first()
    #     # userdata['product_name']= product['product_name'] if product else 0
    #     # userdata['original_amt'] = product['original_amt']
    #     # userdata['referral_code'] = user['invitation_code']
    #     product_data.append(userdata)

    if user:
        return jsonify({
            "success" : True ,
            "how_it_works" : data,
            "exciting_prizes" : prize_data,
            "home_faqs" : home_faqs,
            "rewards_faqs" : rewards_faqs,
            "referrals_faqs" : referrals_faqs,
            "help_and_support" : help_faqs,
            "galaxy_data" : galaxy_data,
            "advertisement_cards" : ad_data,
            "exclusive_perks" : exclusive_perks,
            "conversion_data"  :conversion_rate,
            "product_offer" : product_data
            })


    return ({"message": "An Unexpected error occurred",
             "success" : False,
             }), 400