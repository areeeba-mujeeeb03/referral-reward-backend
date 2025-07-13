from flask import request, jsonify
import datetime

from main_app.models.admin.links import ReferralReward
from main_app.models.user.reward import Reward
from main_app.models.user.user import User


def meteors_to_stars():
    data = request.get_json()
    meteors_debited = data.get("meteors_to_debit")
    stars_credited = data.get("stars_credited")
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()

    if not user:
        return jsonify({"success": False, "message": "User does not exist"})

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
                "message": "Access token has expired"}), 401

    rewards = Reward.objects(user_id = user_id).first()

    conversions = ReferralReward.objects(admin_uid = user.admin_uid).first()

    rate = conversions.conversion_rates["meteor_to_star"]

    if meteors_debited > rewards.current_meteors:
        return jsonify({"message": "You don't have enough meteors to convert in stars", "success" : False} ), 400

    if not meteors_debited % rate == 0 and meteors_debited != (meteors_debited % rate == 0):
        return jsonify({"message": f"Please enter the multiple of {rate}", "success" : False} ), 400

    rewards.update(
        dec__current_meteors = meteors_debited,
        inc__total_stars = stars_credited
    )

    return jsonify({"message": "done", "success" : True} ), 200


def stars_to_currency():
    data = request.get_json()
    stars_debited = data.get("stars_debited")
    currency_credited = data.get("currency_credited")
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()

    if not user:
        return jsonify({"success": False, "message": "User does not exist"})

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
                     "message": "Access token has expired"}), 401

    rewards = Reward.objects(user_id=user_id).first()
    conversions = ReferralReward.objects(admin_uid = user.admin_uid).first()

    rate = conversions.conversion_rates["star_to_meteor"]

    if stars_debited >= rewards.current_meteors:
        return jsonify({"message": "You don't have enough stars to convert in currency", "success" : False} ), 400

    if not stars_debited % rate == 0  and stars_debited != (stars_debited % rate == 0):
        return jsonify({"message": f"Please enter the multiple of {rate}", "success" : False} ), 400

    rewards.update(
        dec__total_stars=stars_debited,
        inc__total_currency=currency_credited,
    )

    return jsonify({"message": "done", "success" : True} ), 200