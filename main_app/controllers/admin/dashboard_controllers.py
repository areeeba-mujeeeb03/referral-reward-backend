import datetime
from flask import request, jsonify
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.links import AppStats
from main_app.models.admin.participants_model import UserData
from main_app.models.user.user import User
from main_app.models.user.referral import Referral
from main_app.models.user.reward import Reward
from main_app.models.admin.error_model import Errors
from main_app.models.admin.product_model import Product
from main_app.utils.user.string_encoding import generate_encoded_string

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def dashboard_stats():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"})

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if hasattr(exist, 'expiry_time') and exist.expiry_time:
        if datetime.datetime.now() > exist.expiry_time:
            return ({"success": False,
                     "message": "Access token has expired",
                     "token": "expired"}), 401

    if exist:
        all_user_data = UserData.objects(admin_uid = admin_uid).first()
        apps_data = AppStats.objects(admin_uid = admin_uid).first()
        sharing_apps_data = []
        if apps_data:
            for app_data in apps_data.apps:
                userdata = {
                    "app_name": app_data.app_name,
                    "total_sent": app_data.total_sent,
                    "successful_registered": app_data.successful_registered
                }
                sharing_apps_data.append(userdata)

        info = {"total_participants" : all_user_data.total_participants,
                "total_referrals" : all_user_data.total_referrals,
                "referral_leads" : all_user_data.referral_leads,
                "completed_referrals" : all_user_data.successful_referrals,
                "currencies_converted" : all_user_data.currencies_converted,
                "vouchers_won" : all_user_data.vouchers_won,
                "coupons_used" : all_user_data.used_coupons,
                "sharing_apps_data" : sharing_apps_data,
                "games_earnings" : all_user_data.game_earnings,
                "referral_earning": all_user_data.referral_earnings,
                "purchases_earnings" : all_user_data.purchases_earnings,
                "milestones_earnings" : all_user_data.milestones_earnings}

        fields_to_encode = ["total_participants","total_referrals","completed_referrals",
                            "currencies_converted","vouchers_won","coupons_used",
                            "sharing_apps_data","games_earnings","referral_earning",
                            "purchases_earnings","milestones_earnings"
                            ]

        res = generate_encoded_string(info, fields_to_encode)
        return ({"success": True,
                 "data": res}), 403


# ---------------------------------------------------------------------------------
def dashboard_participants():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    users = User.objects(admin_uid = admin_uid)
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"})

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if hasattr(exist, 'expiry_time') and exist.expiry_time:
        if datetime.datetime.now() > exist.expiry_time:
            return ({"success": False,
                     "message": "Access token has expired",
                     "token": "expired"}), 401
    users = User.objects()

    data = []

    for user in users:
        user = user.to_mongo().to_dict()
        userdata = {}
        userdata['username'] = user['username']
        userdata['email'] = user['email']
        userdata['mobile_number'] = user['mobile_number']
        userdata['referral_code'] = user['invitation_code']
        referral = Referral.objects(user_id = user['user_id']).first()
        userdata['referral_earning'] = referral['referral_earning'] if referral else 0
        userdata['total_referrals'] = referral['total_referrals']if referral else 0
        userdata['successful_referrals'] = referral['successful_referrals']if referral else 0
        data.append(userdata)

    redemption_data = []
    for user in users:
        user = user.to_mongo().to_dict()
        userdata = {}
        userdata['username'] = user['username']
        userdata['email'] = user['email']
        userdata['mobile_number'] = user['mobile_number']
        reward = Reward.objects(user_id = user['user_id']).first()
        userdata['redeemed_meteors'] = reward['redeemed_meteors']if reward else 0
        userdata['total_vouchers'] = reward['total_vouchers'] if reward else 0
        redemption_data.append(userdata)

    product_data =[]
    for user in users:
        user = user.to_mongo().to_dict()
        userdata = {}
        userdata['username'] = user['username']
        userdata['email'] = user['email']
        userdata['mobile_number'] = user['mobile_number']
        product = Product.objects(uid= product['uid']).first()
        userdata['product_name']= product['product_name'] if product else 0
        userdata['original_amt'] = product['original_amt']
        userdata['referral_code'] = user['invitation_code']
        product_data.append(userdata)

        games_data =[]
        for user in users:
            user = user.to_mongo().to_dict()
            userdata = {}
            userdata['username'] = user['username']
            userdata['email'] = user['email']
            userdata['mobile_number'] = user['mobile_number']
            # game = Game
            userdata['game_name'] = 0
            userdata['last_play_date'] = 0
            userdata['earning_game'] = 0
            userdata['total_earning'] = 0
            games_data.append(userdata)



    return jsonify({"Participants_and_earning_with_referral" : data,
                    "redeem_table" : redemption_data,
                    "purchase_product":product_data}),200


# ------------Error Table

def error_table():
    try:
        logger.info("Create error table API called.")
        data = request.get_json()
        errors = Errors.objects()

        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        exist = Admin.objects(admin_uid=admin_uid).first()

        if not exist:
            return jsonify({"success": False, "message": "User does not exist"})

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(exist, 'expiry_time') and exist.expiry_time:
            if datetime.datetime.now() > exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired",
                         "token": "expired"}), 401

        all_errors = []
        for error in errors:
            error_dict = error.to_mongo().to_dict()
            error_dict.pop('_id', None)
            response = error_dict
            all_errors.append(error_dict)

        return jsonify({
            "message": "Data retrieved successfully",
            "data": all_errors
        }), 200

    except Exception as e:
        logger.error(f"Internal Server Error while saving email.{str(e)}")
        return jsonify({"error": "Internal server error"})
