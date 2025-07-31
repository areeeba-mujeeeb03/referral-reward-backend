import datetime
from flask import request, jsonify
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.campaign_model import Campaign
from main_app.models.admin.links import AppStats
from main_app.models.admin.participants_model import Participants
from main_app.models.user.user import User
from main_app.models.user.referral import Referral
from main_app.models.user.reward import Reward
from main_app.models.admin.error_model import Errors
# from main_app.models.admin.product_model import Product
from main_app.utils.user.string_encoding import generate_encoded_string

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def dashboard_all_campaigns():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        exist = Admin.objects(admin_uid=admin_uid).first()

        if not exist:
            return jsonify({"success": False, "message": "User does not exist"}), 400

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

        camps = Campaign.objects(admin_uid=admin_uid)

        all_campaigns = []

        for c in camps:
            c = c.to_mongo().to_dict()
            c.pop('_id', None)
            all_campaigns.append(c)

        return jsonify({"success": True, "all_campaigns": all_campaigns}), 200
    except Exception as e:
        logger.error(f"Failed to fetch data as {str(e)}")
        return jsonify({"success": False, "message": "Something Went Wrong"}), 500

def dashboard_stats():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    program_id = data.get("program_id")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

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
    check_program = Campaign.objects(program_id = program_id, admin_uid = admin_uid).first()
    if exist:
        all_user_data = Participants.objects(admin_uid = admin_uid, program_id = check_program.program_id).first()
        apps_data = AppStats.objects(admin_uid = admin_uid, program_id = check_program.program_id).first()
        sharing_apps_data = []
        if apps_data:
            for app_data in apps_data.apps:
                userdata = {
                    "app_name": app_data.get("platform"),
                    "total_sent": app_data.get("sent"),
                    "successful_registered": app_data.get("successful"),
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
    program_id = data.get("program_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    exist = Admin.objects(admin_uid=admin_uid).first()


    # if not exist:
    #     return jsonify({"success": False, "message": "User does not exist"}), 400
    #
    # if not access_token or not session_id:
    #     return jsonify({"message": "Missing token or session", "success": False}), 400
    #
    # if exist.access_token != access_token:
    #     return ({"success": False,
    #              "message": "Invalid access token"}), 401
    #
    # if exist.session_id != session_id:
    #     return ({"success": False,
    #              "message": "Session mismatch or invalid session"}), 403
    #
    # if hasattr(exist, 'expiry_time') and exist.expiry_time:
    #     if datetime.datetime.now() > exist.expiry_time:
    #         return ({"success": False,
    #                  "message": "Access token has expired",
    #                  "token": "expired"}), 401

    user = User.objects(admin_uid=admin_uid, program_id=program_id)
    for u in user:
        data = []
        referral_earnings = Referral.objects().order_by('-referral_earning')
        for earnings in referral_earnings:
            user_sort = User.objects(user_id = earnings.user_id).first()
            users = user_sort.to_mongo().to_dict()
            userdata = {}
            userdata['rank'] = "#" + str(len(data) + 1)
            userdata['name'] = users['name']
            userdata['email'] = users['email']
            userdata['mobile_number'] = users['mobile_number']
            userdata['referral_code'] = users['invitation_code']
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
            userdata['name'] = user_sort.name
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
            user_sort = User.objects(user_id = redemption.user_id       ).first()
            # user = user_sort.to_mongo().to_dict()
            userdata = {}
            userdata['rank'] = "#" + str(len(games_data) + 1 )
            userdata['name'] = user_sort.name
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
    if not user:
        return jsonify({"success": True, "message" : "No users registered yet."}), 200

# ------------Error Table

def error_table():
    try:
        logger.info("Create error table API called.")
        data = request.get_json()
        program_id = data.get("program_id")
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        exist = Admin.objects(admin_uid=admin_uid).first()

        if not exist:
            return jsonify({"success": False, "message": "User does not exist"}), 400

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

        camp = Campaign.objects(admin_uid = admin_uid, program_id = program_id).first()

        if not camp:
            return jsonify({"message" : "Campaign Not Found", "success" : False})

        errors = Errors.objects(admin_uid=admin_uid, program_id = program_id)
        all_errors = []
        for error in errors:
            error_dict = error.to_mongo().to_dict()
            error_dict.pop('_id', None)
            error_dict.pop('program_id', None)
            error_dict.pop('admin_uid', None)
            all_errors.append(error_dict)

        return jsonify({
            "message": "Data retrieved successfully",
            "data": all_errors
        }), 200

    except Exception as e:
        logger.error(f"Internal Server Error while saving email.{str(e)}")
        return jsonify({"error": "Internal server error"}),500

def graph_data():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    registered_user = User.objects(admin_uid = admin_uid).order_by('created_at')

    return jsonify({"registrations": registered_user, "success" : True}),200

def reward_history():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    program_id = data.get("program_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

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

    registered_users = User.objects(admin_uid = admin_uid, program_id = program_id)

    reward_data = []

    for registered_user in registered_users:
        user_dict = {}
        user_dict['name'] = registered_user.name
        user_dict['email'] = registered_user.email
        rewards = Reward.objects(user_id = registered_user.user_id).first()
        user_dict['total_rewards'] = len(rewards.reward_history)
        user_dict['earnings'] = rewards.total_meteors_earned
        user_dict['reward_history'] = rewards.reward_history
        reward_data.append(user_dict)

    rank_data = []

    for registered_user in registered_users:
        user_dict = {}
        user_dict['name'] = registered_user.name
        user_dict['email'] = registered_user.email
        rewards = Reward.objects(user_id=registered_user.user_id).first()
        user_dict['total_rewards'] = len(rewards.reward_history)
        user_dict['earnings'] = rewards.total_meteors_earned
        user_dict['reward_history'] = rewards.reward_history
        rank_data.append(user_dict)

    top_referrers = []

    top_ref_data = Referral.objects().order_by('-total_referrals').limit(3)
    for ref in top_ref_data:
        user = User.objects(user_id=ref.user_id, admin_uid = admin_uid, program_id = program_id).first()
        if user:
            top_referrers.append({
                "name": user.name,
                "email": user.email,
                "total_referrals": ref.total_referrals
            })

    # Get top 3 earners
    top_earners = []

    top_earnings = Reward.objects().order_by('-total_stars').limit(3)
    for reward in top_earnings:
        user = User.objects(user_id=reward.user_id, admin_uid = admin_uid, program_id = program_id).first()
        if user and user.admin_uid == admin_uid and user.program_id == program_id:
            top_earners.append({
                "name": user.name,
                "email": user.email,
                "total_meteors_earned": reward.total_stars
            })

    info = {"rewards": reward_data,
        "top_referrers": top_referrers,
        "top_earners": top_earners}
    fields_to_encode = ["rewards", "top_referrers", "top_earners"]

    generate_encoded_string(info, fields_to_encode)
    return jsonify({
        "rewards": reward_data,
        "top_referrers": top_referrers,
        "top_earners": top_earners,
        "success": True
    }), 200