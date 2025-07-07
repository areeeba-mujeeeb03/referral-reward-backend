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

# ---------------------------------------------------------------------------------

#------- Participant Table

def participant_table():
    try:
        logger.info("Create participant table API called.")
        data = request.get_json()
        user_id = data.get("user_id")
        uid = data.get("uid")

        if not user_id:
            return jsonify({"message": "User ID is required"}), 400

        user = User.objects(user_id=user_id).first()
        referral = Referral.objects(user_id=user_id).first()
        reward = Reward.objects(user_id=user_id).first()
        # redeem = Redeem.objects(user_id=user_id).first()
        product = Product.objects(uid=uid).first()

        game = [{
                "usermname": user.username,
                "email": user.email,
                "mobile_number": user.mobile_number
            }]

        refer = [{
            "total_referrals":referral.total_referrals,
            "referral_earning":referral.referral_earning,
            "total_meteors":reward.total_meteors
        }]

        # redemption = [{
        #     "no_of_redeem":redeem.no_of_redeem,
        #     "points_use":redeem.points_use,
        #     "total_points":redeem.total_points
        # }]

        product_purchased = [{
            "product_name":product.product_name,
            "original_amt":product.original_amt,
            # "coupon_code":product.coupon_code,
            # "referral_code":product.referral_code
        }]

        return jsonify ({
            "message": "Data fetch successfull",
            "data": {
                "game": game,
                "refer":refer,
                # "redemption": redemption,
                "product_purchased":product_purchased
            }
        }), 200
    except Exception as e:
        logger.error("Internal Server Error while saving email.")
        return jsonify({"error": "Internal server error"})

# --------------------------------------------------------------------------------------------------

# -------- Push up Notification
# def create_notification():
#     try: 
#         data = 
#         return jsonify({"message": ""})
#     except Exception as e:
#         return jsonify({"error": "Internal server error"})









    # # Get user
    # user = User.objects(user_id=user_id).first()
    # if not user:
    #     return jsonify({"message": "User not found"}), 400

    # user_data = user.to_mongo().to_dict()
    # user_data.pop('_id', None)

    # # Get referral data
    # referral = Referral.objects(user_id=user_id).first()
    # referral_data = referral.to_mongo().to_dict() if referral else {}
    # referral_data.pop('_id', None)

    # # Get reward data
    # reward = Reward.objects(user_id=user_id).first()
    # reward_data = reward.to_mongo().to_dict() if reward else {}
    # reward_data.pop('_id', None)

    # # Get link data
    # link = Link.objects(user_id=user_id).first()
    # link_data = link.to_mongo().to_dict() if link else {}
    # link_data.pop('_id', None)
    # # for user in users :

    # # Combine all into one response
    # response = {
    #     "user": user_data,
    #     "referral": referral_data,
    #     "reward": reward_data,
    #     "link": link_data
    # }

    # return jsonify({
    #     "message": "Data retrieved successfully",
    #     "data": response
    # }), 200




















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
