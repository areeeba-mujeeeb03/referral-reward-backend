import datetime
from itertools import count

from flask import request, jsonify
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.links import AppStats
from main_app.models.admin.participants_model import UserData
from main_app.models.user.user import User
from main_app.models.user.referral import Referral
from main_app.models.user.reward import Reward
from main_app.models.admin.error_model import Errors
# from main_app.models.admin.product_model import Product
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
                    "app_name": app_data.get("app_name"),
                    "total_sent": app_data.get("total_sent"),
                    "successful_registered": app_data.get("successful_registered"),
                    "referral_leads": app_data.get("accepted")
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
                "purchases_earnings" : all_user_data.signup_earnings,
                "milestones_earnings" : all_user_data.milestones_earnings,
                "total_earnings" :all_user_data.milestones_earnings + all_user_data.signup_earnings + all_user_data.referral_earnings + all_user_data.game_earnings}

        fields_to_encode = ["total_participants","total_referrals","referral_leads","completed_referrals",
                            "currencies_converted","vouchers_won","coupons_used",
                            "sharing_apps_data","games_earnings","referral_earning",
                            "purchases_earnings","milestones_earnings", "total_earnings"]

        res = generate_encoded_string(info, fields_to_encode)
        return ({"success": True,
                 "data": res}), 200


# ---------------------------------------------------------------------------------
def dashboard_participants():
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

    data = []

    referral_earnings = Referral.objects().order_by('-referral_earning')
    for earnings in referral_earnings:
        user_sort = User.objects(user_id = earnings.user_id).first()
        user = user_sort.to_mongo().to_dict()
        userdata = {}
        userdata['rank'] = "#" + str(len(data) + 1)
        userdata['username'] = user['username']
        userdata['email'] = user['email']
        userdata['mobile_number'] = user['mobile_number']
        userdata['referral_code'] = user['invitation_code']
        userdata['referral_earning'] = earnings['referral_earning']
        userdata['total_referrals'] = earnings['total_referrals']
        userdata['successful_referrals'] = earnings['successful_referrals']
        earn = Reward.objects(user_id = user_sort.user_id).first()
        userdata['total_earnings'] = earn['total_meteors_earned']
        data.append(userdata)

    redemption_data = []
    redemptions = Reward.objects().order_by('-redeemed_meteors')
    for redemption in redemptions:
        user_sort = User.objects(user_id = redemption.user_id).first()
        userdata = {}
        # userdata['rank'] =  "#" + (len(redemption_data) + 1)
        userdata['rank'] = "#" + str(len(redemption_data) + 1)
        print(userdata['rank'])
        userdata['username'] = user_sort.username
        userdata['email'] = user_sort.email
        userdata['rewards_redeemed'] = redemption.total_meteors_earned,
        userdata['num_of_redemp'] = redemption.used_vouchers,
        userdata['last_redeemed'] = "06-07-2025"
        userdata['points_used'] = redemption.redeemed_meteors
        userdata['current_meteors'] = redemption.current_meteors
        redemption_data.append(userdata)

    # product_data =[]
    # for user in users:
    #     user = user.to_mongo().to_dict()
    #     userdata = {}
    #     userdata['username'] = user['username']
    #     userdata['email'] = user['email']
    #     userdata['mobile_number'] = user['mobile_number']
    #     product = Product.objects().first()
    #     userdata['product_name']= product['product_name'] if product else 0
    #     userdata['original_amt'] = product['original_amt']
    #     userdata['referral_code'] = user['invitation_code']
    #     product_data.append(userdata)

    games_data =[]
    redemptions = Reward.objects().order_by('-redeemed_meteors')
    for redemption in redemptions:
        user_sort = User.objects(user_id = redemption.user_id).first()
        # user = user_sort.to_mongo().to_dict()
        userdata = {}
        userdata['rank'] = "#" + str(len(games_data) + 1 )
        userdata['username'] = user_sort.username
        userdata['email'] = user_sort.email
        userdata['mobile_number'] = user_sort.mobile_number
        # game = Game
        userdata['game_name'] = "SPIN-THE-WHEEL"
        userdata['last_play_date'] = "07-07-2025"
        userdata['earning_game'] = 0
        userdata['total_earning'] = 0
        userdata['num_play'] = 0
        games_data.append(userdata)

    info = {"Participants_and_earning_with_referral": data,
            "redeem_table": redemption_data,
            "games_data" : games_data,
            # "purchase_product": product_data
            # "games_data" : games[]
            }

    fields_to_encode = ["Participants_and_earning_with_referral",
                        "redeem_table",
                        "games_data"]

    res = generate_encoded_string(info, fields_to_encode)

    return jsonify({"success" : True, "data" : res}),200

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

def graph_data(admin_uid):
    registered_user = User.objects(admin_uid = admin_uid).order_by('created_at')

    return jsonify({"registrations": registered_user, "success" : True}),200


