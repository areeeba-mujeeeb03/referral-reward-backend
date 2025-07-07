from flask import request, jsonify

from main_app.models.admin.admin_model import Admin
from main_app.models.admin.participants_model import UserData
from main_app.models.user.user import User
from main_app.models.user.referral import Referral
from main_app.models.user.reward import Reward
from main_app.models.user.links import Link
from main_app.models.admin.error_model import Errors
from main_app.routes.admin.admin_routes import admin_bp


def dashboard_stats():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    exist = Admin.objects(admin_uid = admin_uid).first()
    if exist:
        all_user_data = UserData.objects(admin_uid = admin_uid).first()
        return jsonify({"total_participants" : all_user_data.total_participants,
                        "total_referrals" : all_user_data.succesful_referrals,
                        "completed_referrals" : all_user_data.completed_referrals})
    if not exist:
        return jsonify({"success": False, "message" : "Admin id not found"})
# ------------Error Table

def error_table():
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
        userdata['referral_earning'] = referral['referral_earning']
        userdata['total_referrals'] = referral['total_referrals']
        userdata['successful_referrals'] = referral['successful_referrals']
        data.append(userdata)

    redemption_data = []
    for user in users:
        user = user.to_mongo().to_dict()
        userdata = {}
        userdata['username'] = user['username']
        userdata['email'] = user['email']
        userdata['mobile_number'] = user['mobile_number']
        reward = Reward.objects(user_id = user['user_id']).first()
        userdata['redeemed_meteors'] = reward['redeemed_meteors']
        userdata['total_vouchers'] = reward['total_vouchers']
        redemption_data.append(userdata)

    return jsonify({"Partcipants_and_earning_with_referral" : data, "redeem_table" : redemption_data})

