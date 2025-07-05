from flask import request, jsonify
from main_app.models.user.user import User
from main_app.models.user.referral import Referral
from main_app.models.user.reward import Reward
from main_app.models.user.links import Link
from main_app.models.admin.error_model import Errors

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

# Participant Table

def participant_table():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"message": "User ID is required"}), 400

    user = User.objects(user_id=user_id).first()
    referral = Referral.objects(user_id=user_id).first()
    reward = Reward.objects(user_id=user_id).first()

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

    return jsonify ({
        "message": "Data fetch successfull",
        "data": {
            "game": game,
            "refer":refer
        }
    }), 200

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
