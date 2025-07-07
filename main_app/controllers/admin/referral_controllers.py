from datetime import datetime, timedelta
from flask import jsonify, request
from main_app.models.admin.links import Link


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
        return datetime.fromisoformat(date_str)
    except ValueError:
        try:
            return datetime.strptime("%dd/%mm/%YYYY", "%dd-%mm-%YYYY", )
        except ValueError:
            return None

def generate_invite_link_with_expiry():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    start_date = parse_date_flexible(data.get("start_date"))
    expiry_date = parse_date_flexible(data.get("expiry_date"))
    referrer_reward = data.get("referrer_reward")
    referee_reward = data.get("referee_reward")

    if not start_date or not expiry_date:
        return jsonify({"error": "Start date and expiry date are required"}), 400

    gen_str = int(start_date.strftime("%Y%m%d%H%M%S"))
    expiry_time = expiry_date + timedelta(hours=5)
    exp_str = int(expiry_time.strftime("%Y%m%d%H%M%S"))

    encoded_gen_str = encode_timestamp(gen_str)
    encoded_exp_str = encode_timestamp(exp_str)

    base_url = "http://127.0.0.1:5000/wealth-elite/referral-program/invite_link"
    invitation_link = f"{base_url}/{encoded_gen_str}/{encoded_exp_str}"

    link =Link(
        invitation_link=invitation_link,
        start_date=start_date,
        expiry_date=expiry_date,
        created_at=datetime.now(),
        referrer_reward = referrer_reward,
        referee_reward = referee_reward
    )
    link.save()

    return jsonify({"link": invitation_link}), 200

