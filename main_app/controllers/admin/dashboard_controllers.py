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

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def dashboard_stats():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    exist = Admin.objects(admin_uid = admin_uid).first()
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

        return jsonify({"total_participants" : all_user_data.total_participants,
                        "total_referrals" : all_user_data.succesful_referrals,
                        "completed_referrals" : all_user_data.completed_referrals,
                        "sharing_apps_data" : sharing_apps_data})
    if not exist:
        return jsonify({"success": False, "message" : "Admin id not found"})

# ---------------------------------------------------------------------------------
def dashboard_participants():
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
        # product_uid = Product.get('product_uid')  # Ensure this exists in the user model
        # # if product_uid:
        # product = Product.objects(uid= uid['uid']).first()
        # userdata['product_name']= product['product_name'] if product else 0
        # userdata['original_amt'] = product['original_amt']
        # userdata['referral_code'] = user['invitation_code']
        product_data.append(userdata)

    return jsonify({"Partcipants_and_earning_with_referral" : data, "redeem_table" : redemption_data, "purchase_product":product_data})


# ------------Error Table

def error_table():
    try:
        logger.info("Create error table API called.")
        data = request.get_json()
        errors = Errors.objects()

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
        logger.error("Internal Server Error while saving email.")
        return jsonify({"error": "Internal server error"})



























# def error_table():
#     data = request.get_json()
#     user_id = data.get("user_id")

#     if not user_id:
#         return jsonify({"message": "User ID is required"}), 400

#     user = User.objects(user_id=user_id).first()
#     if not user:
#         return jsonify({"message": "User not found"}), 400

#     user_dict = user.to_mongo().to_dict()
#     user_dict.pop('_id', None)  # Remove MongoDB internal ID

#     return jsonify({
#         "message": "User data retrieved successfully",
#         "data": user_dict
#     }), 200
