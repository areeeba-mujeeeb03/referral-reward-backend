from datetime import datetime, timedelta
from flask import jsonify, request

from main_app.models.admin.admin_model import Admin
from main_app.models.admin.links import Link
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
    except (ValueError, TypeError):
        return None

def generate_invite_link_with_expiry():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    start_date = parse_date_flexible(data.get("start_date"))
    expiry_date = parse_date_flexible(data.get("expiry_date"))
    referrer_reward = data.get("referrer_reward")
    referee_reward = data.get("referee_reward")

    if not admin_uid:
        return jsonify({"error": "admin_uid is required", "success" : False}), 400

    admin = Admin.objects(admin_uid = admin_uid).first()

    if not admin:
        return jsonify({"error" : "User not found", "success" : False}), 404

    if not start_date and not expiry_date:
        return jsonify({"error": "Start date and expiry date are required", "success" : False}), 400

    if not referrer_reward and not referee_reward:
        return jsonify({"error": "Referrer Reward and Referee Reward are required", "success" : False}), 400

    gen_str = int(start_date.strftime("%Y%m%d%H%M%S"))
    expiry_time = expiry_date + timedelta(hours=5)
    exp_str = int(expiry_time.strftime("%Y%m%d%H%M%S"))

    encoded_gen_str = encode_timestamp(gen_str)
    encoded_exp_str = encode_timestamp(exp_str)

    base_url = "http://127.0.0.1:5000/wealth-elite/referral-program/invite_link"

    invitation_link = f"{base_url}/{encoded_gen_str}/{encoded_exp_str}"

    link =Link(
        admin_uid = admin_uid,
        invitation_link=invitation_link,
        start_date=start_date,
        expiry_date=expiry_date,
        created_at=datetime.now(),
        referrer_reward = referrer_reward,
        referee_reward = referee_reward
    )
    link.save()

    is_active = gen_str <= int(datetime.now().strftime("%Y%m%d%H%M%S"))
    link.update(active=is_active)


    return jsonify({"link": invitation_link, "success" : True, "message" : "Link generated"}), 200

