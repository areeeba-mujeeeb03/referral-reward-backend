from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from flask import jsonify

from main_app.utils.user.error_handling import handle_error


def home_page(user_id):
    try:
        user  = User.objects(user_id = user_id).first()
        user_reward = Reward.objects(user_id = user_id).first()
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
        if user :
            return jsonify({"success" : True,
                            "invitation_link"  : User.invitation_link,
                            "data" : {"total_stars" : Reward.total_stars,
                                      "total_meteors" : Reward.total_meteors,
                                      "galaxy_name" : Reward.galaxy_name,
                                      "current_planet" : Reward.current_planet,}
                            })

    except Exception as e:
        return handle_error(e)


def my_rewards(user_id):
    try:
        user  = User.objects(user_id = user_id).first()
        user_reward = Reward.objects(user_id = user_id).first()
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
        if user :
            return jsonify({"success" : True,
                            "invitation_link"  : User.invitation_link,
                            "data" : {"total_stars" : Reward.total_stars,
                                      "total_meteors" : Reward.total_meteors,
                                      "galaxy_name" : Reward.galaxy_name,
                                      "current_planet" : Reward.current_planet,
                                      "total_vouchers" : Reward.total_vouchers,
                                      "reward_history" : Reward.reward_history}
                            })
    except Exception as e:
        return handle_error(e)

def my_referrals(user_id):
    try:
        user  = User.objects(user_id = user_id).first()
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
        if user :
            return jsonify({"success" : True,
                            "invitation_link"  : User.invitation_link,
                            "data" : {"total_referrals" : Referral.total_referrals,
                                      "referral_earning" : Referral.referral_earning,
                                      "pending_referrals" : Referral.pending_referrals,
                                      "all referrals" :Referral.all_referrals}
                            })
    except Exception as e:
        return handle_error(e)

#----------------------------------------------------------------------------------------------------

def my_profile(user_id):
    try:
        user  = User.objects(user_id = user_id).first()
        user_reward = Reward.objects(user_id = user_id).first()
        if not user_id:
            return jsonify({"message" : "Unauthorized User"})
        if not user :
            return jsonify({"message" : "User Not Found", "success": False}), 404
        if user :
            return jsonify({"success" : True,
                            "data" : {"username" : User.mobile_number,
                                      "email" : User.email,
                                      "password" : User.password}
                            })
    except Exception as e:
        return handle_error(e)