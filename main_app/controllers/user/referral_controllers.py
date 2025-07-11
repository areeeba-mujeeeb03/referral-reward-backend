import datetime
import logging
from main_app.controllers.user.rewards_controllers import win_voucher
from main_app.models.admin.error_model import Errors
from main_app.models.admin.links import Link
from main_app.models.admin.participants_model import UserData
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.models.user.user import User
from flask import jsonify, request

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Referral reward points configuration
PENDING_REFERRAL_REWARD_POINTS = 400
SUCCESS_REFERRAL_REWARD_POINTS = 600
SESSION_EXPIRY_MINUTES = 30
SIGN_UP_REWARD = 500

# ==================

# Referral Code Processing Utility

# ==================
galaxies = ['Milky Way Galaxy' , 'Andromeda Galaxy', 'Bear Paw Galaxy', 'Blinking Galaxy', 'Fireworks Galaxy', '']
def process_referral_code_and_reward(referral_code, new_user_id, new_username):
    """
    Process referral code and update referrer's rewards and statistics

    Referral Process:
    1. Find user who owns the referral code
    2. Update referrer's referral statistics
    3. Add reward points to referrer's account
    4. Record referral transaction with pending status

    Args:
        referral_code (str): Referral code provided during registration
        new_user_id (str): ID of the newly registered user
    """
    valid_code = User.objects(invitation_code=referral_code).first()
    try:
        referrer_id = str(valid_code.user_id)
        if valid_code:
            referrer = Referral.objects(user_id = referrer_id).first()
            new_user = User.objects(user_id = new_user_id)
            date = datetime.datetime.now()
            referrer.update(
                push__all_referrals={
                    "username" : new_username,
                    "user_id": new_user_id,
                    "referral_status": "Pending",
                    "date" : date.strftime('%d-%m-%y'),
                    "earned_meteors" : PENDING_REFERRAL_REWARD_POINTS

                },
                inc__total_referrals = 1,
                inc__pending_referrals=1,
                inc__referral_earning = PENDING_REFERRAL_REWARD_POINTS
            )


            reward_record = Reward.objects(user_id=referrer_id).first()
            UserData.objects().first()
            new_user = User.objects(user_id = new_user_id).first()
            if reward_record:
                reward_record.total_meteors += PENDING_REFERRAL_REWARD_POINTS
                reward_record.reward_history.append({
                    "earned_by_action": "referral",
                    "earned_meteors": PENDING_REFERRAL_REWARD_POINTS,
                    "referred_to" : new_user.username,
                    "referral_status": "pending",
                    "referred_on": date.strftime('%d-%m-%y'),
                    "transaction_type": "credit"})
                reward_record.save()

    except Exception as e:
        Errors(username=valid_code.user_id, email=valid_code.email, error_source="Sign Up Form",
               error_type=f"Failed to initialize user records : {valid_code.user_id}").save()
        logger.error(f"Failed to initialize user rewards : {str(e)}")
        return jsonify({"message" : "Failed to initialize user rewards.", "success" : False})


def process_tag_id_and_reward(tag_id, new_user_id):
    """
    Process referral code and update referrer's rewards and statistics

    Referral Process:
    1. Find user who owns the referral code
    2. Update referrer's referral statistics
    3. Add reward points to referrer's account
    4. Record referral transaction with pending status

    Args:
        tag_id : attached in API
    """
    valid_user = User.objects(tag_id=tag_id).first()
    referrer = Referral.objects(user_id=valid_user.user_id).first()
    try:
        valid_user = User.objects(tag_id = tag_id).first()
        referrer = Referral.objects(user_id = valid_user.user_id).first()
        referrer.save()
        new_user = User.objects(user_id = new_user_id).first()
        if new_user:
            new_user.update(
                set__referred_by = valid_user.user_id
            )
        date = datetime.datetime.now()
        referrer.update(
            push__all_referrals={
                "username" : new_user.username,
                "user_id": new_user_id,
                "email" : new_user.email,
                "referral_status": "Pending",
                "date" : date.strftime('%d-%m-%y'),
                "earned_meteors" : PENDING_REFERRAL_REWARD_POINTS
            },
            inc__total_referrals = 1,
            inc__pending_referrals=1,

        )
        reward_record = Reward.objects(user_id=valid_user.user_id).first()
        if reward_record:
            reward_record.total_meteors += PENDING_REFERRAL_REWARD_POINTS
            reward_record.reward_history.append({
                "earned_by_action": "referral",
                "earned_meteors": PENDING_REFERRAL_REWARD_POINTS,
                "referred_to" : new_user.username,
                "referral_status": "pending",
                "referred_on": date.strftime('%d-%m-%y'),
                "transaction_type": "credit"
            })
            reward_record.save()

    except Exception as e:
        Errors(username=valid_user.user_id, email=valid_user.email, error_source="Referee Sign Up Form",
               error_type=f"Failed to update referrer records of referrer {valid_user.user_id}").save()
        logger.error(f"Failed to update referrer records of referrer {valid_user.user_id}.: {str(e)}")


def update_referral_status_and_reward(referrer_id, user_id):

    """
    Update referrer's referral statistics and tracking records.

    Args:
        referrer_id (str): ID of the user who referred
        user_id (str): ID of the newly registered user
    """
    # Load the referrer’s referral document
    referral_record = Referral.objects(user_id=referrer_id).first()
    if not referral_record:
        logger.warning(f"No referral record found for referrer: {referrer_id}")
        return

    # Find and update the matching referral entry
    referral_found = False
    already_completed = False

    for referral in referral_record.all_referrals:
        if referral.get("user_id") == user_id:
            referral_found = True
            if referral.get("referral_status") == "Completed":
                already_completed = True
            else:
                referral["referral_status"] = "Completed"
                referral["earned_meteors"] = referral.get("earned_meteors", 0) + SUCCESS_REFERRAL_REWARD_POINTS
            break

    if not referral_found:
        logger.warning(f"No matching referral entry for user_id: {user_id} under referrer: {referrer_id}")
        return

    if already_completed:
        logger.info(f"Referral already marked completed for user {user_id}")
        return

    referral_record.all_referrals = referral_record.all_referrals
    # Update
    referral_record.referral_earning += SUCCESS_REFERRAL_REWARD_POINTS
    referral_record.pending_referrals = max(0, referral_record.pending_referrals - 1)
    referral_record.successful_referrals = max(0, referral_record.successful_referrals + 1)
    referral_record.save()
    logger.info(f"Referral stats updated for referrer: {referrer_id}")

    # Now update the referrer’s reward
    reward_record = Reward.objects(user_id=referrer_id).first()
    new_user_reward = Reward.objects(user_id=user_id).first()
    new_user_reward.update(
        inc__current_meteors = 500,
        inc__total_meteors_earned = 500
    )
    if not reward_record:
        logger.warning(f"No reward record found for user: {referrer_id}")
        return

    already_rewarded = any(
        entry.get("earned_by_action") == "referral" and
        entry.get("referral_status") == "Completed" and
        entry.get("referred_user_id") == user_id
        for entry in reward_record.reward_history
    )

    if already_rewarded:
        logger.info(f"Reward already credited for referral of user {user_id}")
        return
    date = datetime.datetime.now()
    # Append a new reward entry
    reward_record.total_meteors += SUCCESS_REFERRAL_REWARD_POINTS
    reward_record.reward_history.append({
        "earned_by_action": "referral",
        "earned_meteors": SUCCESS_REFERRAL_REWARD_POINTS,
        "referral_status": "Completed",
        "referred_user_id": user_id,
        "referred_on": date.strftime('%d-%m-%y'),
        "transaction_type": "credit"
    })
    win_voucher(referrer_id)
    reward_record.save()
    logger.info(f"Reward added for referrer: {referrer_id}")



def initialize_user_records(user_id):
    """
    Initialize empty reward and referral tracking records for new user

    Args:
        user_id (str): ID of the newly registered user
    """
    user_rewards = Reward.objects(user_id=user_id).first()
    user_referrals = Referral.objects(user_id=user_id).first()
    user = User.objects(user_id=user_id).first()
    print(user_id)
    try:
        if user_referrals and user_rewards :
            return "The rewards for this user is already initialized", False

        user_reward = Reward(
            user_id=user_id,
            reward_history=[],
        )
        user_reward.save()
        user_referral = Referral(user_id = user_id,
                                 all_referrals=[])
        user_referral.save()
        reward = Reward.objects(user_id = user_id).first()
        reward.update(
            inc__total_meteors = SIGN_UP_REWARD,
            redeemed_meteors = 0,
            push__galaxy_name= 'Milky Way Galaxy',
            push__current_planet='Planet A'
        )
        user_referral.update(
            total_referrals=0,
            referral_earning=0,
            pending_referrals=0,
            successful_referrals=0
        ).save()

        logger.info(f"Initialized reward and referral records for user: {user_id}")

    except Exception as e:
        Errors(username=user.user_id, email=user.email, error_source="Sign Up Form",
               error_type=f"Failed to initialize user records for {user_id}").save()
        logger.error(f"Failed to initialize user records for {user_id}: {str(e)}")


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
def change_invite_link():
    """Args:
        tag_id (str): ID of the user referring
    """
    data = request.get_json()
    link = data.get("link")
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()

    if not user:
        return jsonify({"success" : False, "message" : "User does not exist"})

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

    tag_id = user.tag_id

    default_invitation_link = user.invitation_link

    link = Link.objects(invitation_link = link)


    if not link:
        return jsonify({"message": "No special link generated yet", "success" : False}), 404

    user_link = link.invitation_link + f"/{tag_id}"

    user.update(
        set__invitation_link=user_link,
    )
    expiry = link.expiry_date
    base_url = "https://wealthelite.com/invite_link"
    if expiry < datetime.datetime.now():
        user.update(
            set__invitation_link =f"{base_url}/{tag_id}"
        )
        return jsonify({"message": "No special link generated yet", "success": False}), 404

    return jsonify({"success" : True, "message" : "Invitation Link Changed"})

def update_meteors_and_stars():


    return jsonify({})


# ==================

# Handles rewards for special offer

# ==================

def reward_referrer_by_tag(tag_id):
    user = User.objects(tag_id=tag_id).first()
    try:
        data = request.get_json()
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

        referral = Referral.objects(user_id = user.user_id).first()
        referrer_id = user.user_id

        reward_record = Reward.objects(user_id=referrer_id).first()
        if not reward_record:
            return False, "No reward record found for referrer"

        already_rewarded = any(
            entry.get("earned_by_action") == "link_visit"
            for entry in reward_record.reward_history
        )

        if already_rewarded:
            return False, "Reward already claimed for this referral link"
        date = datetime.datetime.now()
        reward_record.total_meteors += SUCCESS_REFERRAL_REWARD_POINTS
        reward_record.reward_history.append({
            "earned_by_action": "link_visit",
            "earned_meteors": SUCCESS_REFERRAL_REWARD_POINTS,
            "referral_status": "Visited",
            "referred_user_id": "anonymous",
            "referred_on": date.strftime('%d-%m-%y'),
            "transaction_type": "credit"
        })
        reward_record.save()
        referral.update(
            inc__successful_referrals = 1
        )
        return True, "Referral reward granted successfully"
    except Exception as e:
        Errors(username=user.user_id, email=user.email, error_source="Sign Up Form",
               error_type=f" Invalid invitation link {user.user_id}").save()
        return jsonify({"message" : "Invalid link"})

def handle_invitation_visit(encoded_gen_str, tag_id, encoded_exp_str):
    """Args:
        tag_id (str): ID of the user referring
        encoded_gen_str : generation time of link
        encoded_exp_str : expiry time of link
    """
    user = User.objects(tag_id = tag_id).first()
    try:
        decoded_gen_str = decode_timestamp(encoded_gen_str)
        decoded_exp_str = decode_timestamp(encoded_exp_str)


        now = datetime.datetime.utcnow()
        now_timestamp = int(now.strftime("%Y%m%d%H%M%S"))

        if now_timestamp > decoded_exp_str:
            return jsonify({"message": "This link has expired"}), 400

        success, msg = reward_referrer_by_tag(tag_id)
        return jsonify({"message": msg}), 200 if success else 400

    except Exception as e:
        Errors(username=user.user_id, email=user.email, error_source="Sign Up Form",
               error_type=f"Expired or Invalid referral link : {user.user_id}").save()
        return jsonify({"message": "Expired or Invalid referral link"}), 400
