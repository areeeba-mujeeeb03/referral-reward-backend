import datetime
from flask import jsonify
from main_app.models.admin.links import Link
# ==================

# Special invitation link with expiry

# ==================

##-------------------------------------Encryption of timestamp-----------------------------------------------##
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


##-------------------------------------Decryption of timestamp-----------------------------------------------##
def decode_timestamp(encoded_string):
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base = len(alphabet)
    number = 0
    for char in encoded_string:
        number = number * base + alphabet.index(char)
    return number

##---------------------------GENERATION OF INVITATION LINK------------------------------------------##
def generate_invite_link_with_expiry(tag_id):
    """Args:
        tag_id (str): ID of the user referring
    """
    now = datetime.datetime.utcnow()
    gen_str = int(now.strftime("%Y%m%d%H%M%S"))
    expiry_time = now + datetime.timedelta(hours=5)
    exp_str = int(expiry_time.strftime("%Y%m%d%H%M%S"))


    encoded_gen_str = encode_timestamp(gen_str)
    encoded_exp_str = encode_timestamp(exp_str)

    base_url = "http://127.0.0.1:5000/wealth-elite/referral-program/invite_link"
    invitation_link = f"{base_url}/{encoded_gen_str}/{tag_id}/{encoded_exp_str}"

    Link.update(
        set__invitation_link=invitation_link,
        set__start_time=gen_str,
        set__expiry_time=exp_str,
        created_at = datetime.datetime.now()
    )

    return jsonify("Discover Wealth Elite — a platform I personally use and trust.\n"
                   "Join via my invitation to access exclusive rewards and product offers.\n"
                   f"Start here: {invitation_link}")

