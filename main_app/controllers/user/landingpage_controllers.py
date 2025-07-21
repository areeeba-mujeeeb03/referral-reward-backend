import datetime
from main_app.controllers.admin.help_request_controllers import get_faqs_by_category_name
from main_app.controllers.user.rewards_controllers import update_planet_and_galaxy
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.error_model import Errors
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.admin.how_it_work_model import HowItWork
from main_app.models.admin.links import ReferralReward
from main_app.models.admin.special_offer_model import Offer
from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.utils.user.error_handling import get_error
import logging
from flask import request, jsonify
from main_app.utils.user.string_encoding import generate_encoded_string
from main_app.models.admin.product_model import Product
from main_app.models.admin.product_offer_model import ProductOffer
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
                            "message" : "User does not exist"}),400

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
            return jsonify({"success" : False, "message" : "User does not exist"}),400

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
        # update_planet_and_galaxy(user_id)

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
                "total_meteors_earned": reward.total_meteors_earned,
                "discount_coupons" : reward.discount_coupons

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
                                "discount_coupons"
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
            return jsonify({"success" : False, "message" : "User does not exist"}),400

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
        # update_planet_and_galaxy(user_id)
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
    # access_token = data.get("mode")
    # session_id = data.get("log_alt")
    #
    user = User.objects(user_id=user_id).first()
    # try:
    #     if not user:
    #         return jsonify({"success" : False, "message" : "User does not exist"}),400
    #
    #     if not access_token or not session_id:
    #         return jsonify({"message": "Missing token or session", "success": False}), 400
    #
    #     if user.access_token != access_token:
    #         return ({"success": False,
    #                  "message": "Invalid access token"}), 401
    #
    #     if user.session_id != session_id:
    #         return ({"success": False,
    #                  "message": "Session mismatch or invalid session"}), 403
    #
    #     if hasattr(user, 'expiry_time') and user.expiry_time:
    #         if datetime.datetime.now() > user.expiry_time:
    #             return ({"success": False,
    #                      "message": "Access token has expired",
    #                         "token"  : "expired"}), 401

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
        if user.referred_by:
            referrer = User.objects(user_id = user.referred_by).first()
            info["referred_by"] = referrer.username
            fields_to_encode.append("referred_by")

        encoded_str = generate_encoded_string(info, fields_to_encode)
        update_planet_and_galaxy(user_id)
        return encoded_str, 200

    # except Exception as e:
    #     # Errors(username = user.username, email = user.email,
    #     #        error_source = "Sign Up Form", error_type = "server_error").save()
    #     logger.error(f"Server Error: {str(e)}")
    #     return jsonify({"error": get_error("server_error")}), 500


# -------------------------------------------------------------------------

def fetch_data_from_admin():
    data = request.get_json()
    user_id = data.get("user_id")
    user = User.objects(user_id = user_id).first()
    admin = Admin.objects(admin_uid = user.admin_uid).first()


    if not user:
        return jsonify({"success": False, "message" : "User does not exist"}),400

    admin_uid = user.admin_uid
    home_faqs = get_faqs_by_category_name(admin_uid, "Home Screen") or []
    rewards_faqs = get_faqs_by_category_name(admin_uid, "Rewards") or []
    referrals_faqs = get_faqs_by_category_name(admin_uid, "Referrals") or []
    help_faqs = get_faqs_by_category_name(admin_uid, "Help and Support FAQs") or []

    how_it_works_text = HowItWork.objects(admin_uid=admin_uid).first()

    if not how_it_works_text:
        return ({"message": "No 'how it works' data found", "success": False}), 404

    how_text = how_it_works_text.to_mongo().to_dict()
    data =[]
    how_text.pop('_id', None)
    how_text.pop('admin_uid', None)
    data.append(how_text)

    prize = AdminPrizes.objects(admin_uid=admin_uid).first()
    pri = prize.prizes
    prize_data = []

    for priz in prize.prizes:
        prize_dict = {}
        prize_dict['prize_id'] = priz['prize_id']
        prize_dict['title'] = priz['title']
        prize_dict['term_conditions'] = priz['term_conditions']
        prize_dict['required_meteors'] = priz['required_meteors']
        prize_dict['product_uid'] = priz['product_uid']
        prize_data.append(prize_dict)

    reward = Reward.objects(user_id=user_id).first()

    current_galaxy_name = reward.galaxy_name[-1]
    galaxy = Galaxy.objects(galaxy_name=current_galaxy_name).first()

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

    ad_data = []
    ad_record = AdminAdvertisementCard.objects(admin_uid=admin_uid).first()
    if ad_record:
        for ad in ad_record.advertisement_cards:
            ad_dict = {
                "title": ad.title,
                "description": ad.description,
                "button_txt": ad.button_txt,
                "image_url": ad.image
            }
            ad_data.append(ad_dict)

    conversion_rate = []
    rates = ReferralReward.objects(admin_uid = user.admin_uid).first()
    conversion_data = {
        "conversion_rates" : rates.conversion_rates,
        "referrer_reward" : rates.referrer_reward,
        "invitee_reward" : rates.invitee_reward,
    }
    conversion_rate.append(conversion_data)

    exclusive_perks = {}

    product_data =[]
    special_offer = {}
    offer = Offer.objects(admin_uid = admin_uid).first()
    if offer and offer.special_offer:
        for offer in offer.special_offer:
            if offer['active'] is True:
                special_offer['title'] = offer['offer_title']
                special_offer['tag'] = offer['tag']
                special_offer['offer_code'] = offer['offer_code']
                special_offer['pop_up_text'] = offer['pop_up_text']
                special_offer['offer_desc'] = offer['offer_desc']

    offer = ProductOffer.objects(admin_uid=admin_uid).first()
    offer_data = []

    for p in offer.offers:
        offer_dict = {}
        offer_dict['off_percent'] = p['off_percent']
        offer_dict['offer_name'] = p['offer_name']
        offer_dict['button_txt'] = p['button_txt']
        offer_dict['one_liner'] = p['one_liner']
        offer_dict['product_uid'] = p['product_uid']
        offer_data.append(offer_dict)

    reward = Reward.objects(user_id=user_id).first()

    diction = {
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
    "product_offer" : product_data,
    "special_offer" : special_offer,
    "exclusive_offers" : offer_data
    }

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
        "product_offer" : product_data,
        "special_offer" : special_offer,
        "exclusive_offers" : offer_data
        })

    return ({"message": "An Unexpected error occurred",
             "success" : False,
             }), 400