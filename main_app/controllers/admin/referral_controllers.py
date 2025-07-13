from datetime import datetime, timedelta
from flask import jsonify, request
import datetime
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.links import Link, AppStats
from dateutil import parser as date_parser

# ==================

# Special invitation link with expiry

# ==================

# Encoding timestamp
def encode_timestamp(number):
    if not isinstance(number, int):
        raise TypeError("Input must be an integer.")

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)

    if number == 0:
        return alphabet[0]

    encoded_string = ""
    while number > 0:
        remainder = number % base
        encoded_string = alphabet[remainder] + encoded_string
        number //= base
    return encoded_string

# Decoding timestamp
def decode_timestamp(encoded_string):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)
    number = 0
    for char in encoded_string:
        number = number * base + alphabet.index(char)
    return number

def parse_date_flexible(date_str):
    if not date_str:
        return None

    try:
        return date_parser.parse(date_str)
    except Exception as e:
        return str(e)

def generate_invite_link_with_expiry():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    start_date = parse_date_flexible(data.get("start_date"))
    expiry_date = parse_date_flexible(data.get("expiry_date"))

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

    if not admin_uid:
        return jsonify({"error": "admin_uid is required", "success" : False}), 400

    admin = Admin.objects(admin_uid = admin_uid).first()

    if not admin:
        return jsonify({"error" : "User not found", "success" : False}), 404

    if not start_date and not expiry_date:
        return jsonify({"error": "Start date and expiry date are required", "success" : False}), 400

    gen_str = int(start_date.strftime("%Y%m%d%H%M%S"))
    expiry_time = expiry_date + timedelta(hours=5)
    exp_str = int(expiry_time.strftime("%Y%m%d%H%M%S"))

    encoded_gen_str = encode_timestamp(gen_str)
    encoded_exp_str = encode_timestamp(exp_str)

    base_url = "http://127.0.0.1:5000/wealth-elite/referral-program/invite_link"

    invitation_link = f"{base_url}/{encoded_gen_str}/{encoded_exp_str}"
    is_active = gen_str <= int(datetime.now().strftime("%Y%m%d%H%M%S"))
    return jsonify({"link": invitation_link, "active": is_active,"success" : True, "message" : "Link generated"}), 200

def save_referral_data():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    referrer_reward_type = data.get("referrer_reward_type")
    referrer_reward_value = data.get("referrer_reward_value")
    referee_reward_type = data.get("referee_reward_type")
    referee_reward_value = data.get("referee_reward_value")
    reward_condition = data.get("reward_condition")
    success_reward = data.get("success_reward")
    invite_link = data.get("invitation_link")
    active  = data.get("active")

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

    missing_fields = [admin_uid,
                      start_date,
                      end_date,
                      referrer_reward_type,
                      referrer_reward_value,
                      referee_reward_type,
                      referee_reward_value,
                      reward_condition,
                      success_reward,
                      invite_link,
                      active
                      ]

    if not missing_fields:
        return jsonify({
            "success": False,
            "error": "Missing required field"
        }), 400

    data = Link(
        admin_uid=admin_uid,
        start_date=start_date,
        end_date=end_date,
        invitation_link=invite_link,
        created_at=datetime.now(),
        referrer_reward_type=referrer_reward_type,
        referrer_reward_value=referrer_reward_value,
        referee_reward_type=referee_reward_type,
        referee_reward_value=referee_reward_value,
        reward_condition=reward_condition,
        success_reward=success_reward,
        active=active
    )
    data.save()

    return jsonify({
        "success": True,
        "message": "Referral setup saved successfully"
    }), 200


def sharing_app_stats():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    platforms = data.get("platforms", [])
    invite_message = data.get("invite_message")
    primary_platform = data.get("primary_platform")

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

    if not admin_uid or not platforms:
        return jsonify({
            "success": False,
            "error": "admin_uid and platform are required"
        }), 400

    stats = AppStats.objects(admin_uid=admin_uid).first()

    if not stats:
        stats = AppStats(admin_uid=admin_uid, apps=[])

    existing_platforms = {}
    for app in stats.apps:
        existing_platforms[app["platform"]] = app

    for platform in platforms:
        if platform not in existing_platforms:
            stats.apps.append({
                "platform": platform,
                "sent": 0,
                "accepted": 0 ,
                "successful":0
            })

    if primary_platform:
        stats.primary_platform = primary_platform
    if invite_message:
        stats.invite_message = invite_message

    stats.save()

    return jsonify({
        "success": True,
        "message": "Updated for platform"
    }), 200
