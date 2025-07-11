from flask import request, jsonify
import datetime

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
    print(user.email)
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

    rewards.update(
        dec__total_meteors = meteors_debited,
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
    print(user.email)
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

    rewards.update(
        dec__total_stars=stars_debited,
        inc__total_currency=currency_credited,
    )

    return jsonify({"message": "done", "success" : True} ), 200