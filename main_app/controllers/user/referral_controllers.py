import datetime
import logging
from main_app.controllers.user.rewards_controllers import win_voucher
from main_app.models.admin.error_model import Errors
from main_app.models.admin.links import Link, ReferralReward
from main_app.models.admin.participants_model import Participants
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.models.user.user import User
from flask import jsonify, request

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Referral reward points configuration
PENDING_REFERRAL_REWARD_POINTS = 400
SUCCESS_REFERRAL_REWARD_POINTS = 400
SESSION_EXPIRY_MINUTES = 30

# ==================

# Referral Code Processing Utility

# ==================
galaxies = ['Milky Way Galaxy' , 'Andromeda Galaxy', 'Bear Paw Galaxy', 'Blinking Galaxy', 'Fireworks Galaxy']
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
    referrer  = valid_code.user_id
    try:
        referrer_id = valid_code.user_id
        if valid_code:
            referrer = Referral.objects(user_id = referrer_id).first()
            new_user = User.objects(user_id = new_user_id).first()
            date = datetime.datetime.now()
            referrer.update(
                push__all_referrals={
                    "name" : new_username,
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
            reward_record.update(
                inc__total_meteors_earned = PENDING_REFERRAL_REWARD_POINTS
            )
            Participants.objects().first()
            if reward_record:
                reward_record.total_meteors += PENDING_REFERRAL_REWARD_POINTS
                reward_record.reward_history.append({
                    "earned_by_action": "referral",
                    "earned_meteors": PENDING_REFERRAL_REWARD_POINTS,
                    "referred_to" : new_user.name,
                    "referral_status": "pending",
                    "referred_on": date.strftime('%d-%m-%y'),
                    "transaction_type": "credit"})
                reward_record.save()
            admin = Participants.objects(admin_uid=referrer.admin_uid, program_id = referrer.program_id).first()
            if admin:
                admin.update(inc__total_referrals=1,
                             inc__referral_leads = 1,
                             inc__referral_earnings = PENDING_REFERRAL_REWARD_POINTS)

    except Exception as e:
        Errors(name=valid_code.name, email=valid_code.email, error_source="Sign Up Form",
               error_type=f"Failed to initialize user records : {valid_code.user_id}").save()
        logger.error(f"Failed to initialize user rewards : {str(e)}")
        return jsonify({"message" : "Failed to initialize user rewards.", "success" : False})

def process_referrer_by_tag_id(tag_id, new_user_id, new_username):
    user = User.objects(tag_id=tag_id).first()
    ref  = Referral.objects(user_id = user.user_id).first()
    if not ref:
        logger.error(f"No referral record for user {user.name}")
        return
    new_user = User.objects(user_id = new_user_id).first()
    if new_user:
        new_user.update(
            set__referred_by=user.user_id
        )

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    ref.update(
        push__all_referrals={
            "name": new_username,
            "user_id": new_user_id,
            "referral_status": "Pending",
            "date": date_str,
            "earned_meteors": PENDING_REFERRAL_REWARD_POINTS
        },
        inc__total_referrals=1,
        inc__pending_referrals=1,
        inc__referral_earning=PENDING_REFERRAL_REWARD_POINTS
    )
    reward = Reward.objects(user_id=ref.user_id).first()
    if reward:
        reward.update(
            inc__total_meteors_earned=PENDING_REFERRAL_REWARD_POINTS
        )
        reward.current_meteors += PENDING_REFERRAL_REWARD_POINTS
        reward.reward_history.append({
            "earned_by_action": "referral",
            "earned_meteors": PENDING_REFERRAL_REWARD_POINTS,
            "referred_to": new_username,
            "referral_status": "Pending",
            "referred_on": date_str,
            "transaction_type": "credit"
        })
        reward.unused_vouchers = getattr(reward, "unused_vouchers", 0)
        reward.save()

    admin = Participants.objects(admin_uid=user.admin_uid, program_id = user.program_id).first()
    if admin:
        admin.update(
            inc__total_participants=1,
            inc__referral_leads=1,
            inc__referral_earnings=PENDING_REFERRAL_REWARD_POINTS
        )

# def process_tag_id_and_reward(tag_id, new_user_id):
#     """
#     Process referral code and update referrer's rewards and statistics
#
#     Referral Process:
#     1. Find user who owns the referral code
#     2. Update referrer's referral statistics
#     3. Add reward points to referrer's account
#     4. Record referral transaction with pending status
#
#     Args:
#         tag_id : attached in API
#     """
#     valid_user = User.objects(tag_id=tag_id).first()
#     referrer = Referral.objects(user_id=valid_user.user_id).first()
#     try:
#         valid_user = User.objects(tag_id = tag_id).first()
#         referrer = Referral.objects(user_id = valid_user.user_id).first()
#         referrer.save()
#         new_user = User.objects(user_id = new_user_id).first()
#         if new_user:
#             new_user.update(
#                 set__referred_by = valid_user.user_id
#             )
#         date = datetime.datetime.now()
#         referrer.update(
#             push__all_referrals={
#                 "username" : new_user.username,
#                 "user_id": new_user_id,
#                 "email" : new_user.email,
#                 "referral_status": "Pending",
#                 "date" : date.strftime('%d-%m-%y'),
#                 "earned_meteors" : PENDING_REFERRAL_REWARD_POINTS
#             },
#             inc__total_referrals = 1,
#             inc__pending_referrals=1,
#
#         )
#         reward_record = Reward.objects(user_id=valid_user.user_id).first()
#         reward_record.update(
#             inc__total_meteors_earned=PENDING_REFERRAL_REWARD_POINTS
#         )
#         if reward_record:
#             reward_record.total_meteors += PENDING_REFERRAL_REWARD_POINTS
#             reward_record.reward_history.append({
#                 "earned_by_action": "referral",
#                 "earned_meteors": PENDING_REFERRAL_REWARD_POINTS,
#                 "referred_to" : new_user.username,
#                 "referral_status": "pending",
#                 "referred_on": date.strftime('%d-%m-%y'),
#                 "transaction_type": "credit"
#             })
#             reward_record.save()
#             admin = UserData.objects(admin_uid=referrer.admin_uid).first()
#             if admin:
#                 admin.update(inc__total_participants = 1,
#                              inc__total_referrals=1,
#                              inc__referral_leads=1,
#                              inc__referral_earnings=PENDING_REFERRAL_REWARD_POINTS)
#
#     except Exception as e:
#         Errors(username=valid_user.user_id, email=valid_user.email, error_source="Referee Sign Up Form",
#                error_type=f"Failed to update referrer records of referrer {valid_user.user_id}").save()
#         logger.error(f"Failed to update referrer records of referrer {valid_user.user_id}.: {str(e)}")


def update_referral_status_and_reward(referrer_id, user_id):
    ref = Referral.objects(user_id=referrer_id).first()
    referrer = User.objects(user_id = referrer_id)
    if not ref:
        logger.warning(f"No referral record for {referrer_id}")
        return

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    for item in ref.all_referrals:
        if item["user_id"] == user_id and item["referral_status"] != "Completed":
            item["referral_status"] = "Completed"
            item["earned_meteors"] += SUCCESS_REFERRAL_REWARD_POINTS
            break
    else:
        return

    ref.pending_referrals = max(0, ref.pending_referrals - 1)
    ref.successful_referrals += 1
    ref.referral_earning += SUCCESS_REFERRAL_REWARD_POINTS
    ref.save()

    reward = Reward.objects(user_id=referrer_id).first()
    new_user = User.objects(user_id = user_id).first()
    new_user.update(
        referred_by = referrer_id
    )

    if reward:
        reward.current_meteors += SUCCESS_REFERRAL_REWARD_POINTS
        reward.total_meteors_earned += SUCCESS_REFERRAL_REWARD_POINTS
        rewards = ReferralReward.objects(admin_uid=referrer.admin_uid, program_id=referrer.program_id).first()
        if rewards.referrer_reward_type == "meteors":
            reward.reward_history.append({
            "earned_by_action": "referral_success",
            "earned_meteors": rewards.referrer_reward + "meteors",
            "referral_status": "Completed",
            "referred_user_id": user_id,
            "referred_on": date_str,
            "transaction_type": "credit"
        })
        if rewards.referrer_reward_type == "stars":
            reward.reward_history.append({
            "earned_by_action": "referral_success",
            "earned_meteors": rewards.referrer_reward + "stars",
            "referral_status": "Completed",
            "referred_user_id": user_id,
            "referred_on": date_str,
            "transaction_type": "credit"
        })
        if rewards.referrer_reward_type == "currency":
            reward.reward_history.append({
            "earned_by_action": "referral_success",
            "earned_meteors": rewards.referrer_reward + "currency",
            "referral_status": "Completed",
            "referred_user_id": user_id,
            "referred_on": date_str,
            "transaction_type": "credit"
        })
        reward.save()

    user = User.objects(user_id=user_id).first()
    if user:
        update_referrer_stats(user.admin_uid, user)

    voucher_given = win_voucher(referrer_id)
    logger.info(f"Voucher reward {'granted' if voucher_given else 'not granted'} to {referrer_id}")


def update_referrer_stats(admin_uid, user):
    """
    Update global admin referral statistics after a successful referral.

    Args:
        admin_uid (str): Admin UID under whom the referrer and referee are registered
    """
    admin = Participants.objects(admin_uid=admin_uid, program_id = user.program_id).first()
    if not admin:
        logger.warning(f"Admin not found for UID: {admin_uid}")
        return
    reward = Participants.objects(admin_uid=user.admin_uid, program_id=user.program_id).first()
    signup_reward = reward.signup_reward
    if reward.signup_reward_type == "meteors" :
        try:
            admin.update(
                inc__successful_referrals=1,
                inc__signup_earnings=signup_reward,
                inc__total_participants=1
            )
            logger.info(f"Admin stats updated for UID: {admin_uid}")
        except Exception as e:
            logger.error(f"Failed to update admin stats for UID: {admin_uid} — {str(e)}")
    if reward.signup_reward_type == "stars" :
        try:
            admin.update(
                inc__successful_referrals=1,
                inc__signup_earnings=signup_reward,
                inc__total_participants=1
            )
            logger.info(f"Admin stats updated for UID: {admin_uid}")
        except Exception as e:
            logger.error(f"Failed to update admin stats for UID: {admin_uid} — {str(e)}")

    if reward.signup_reward_type == "currency" :
        try:
            admin.update(
                inc__successful_referrals=1,
                inc__signup_earnings=signup_reward,
                inc__total_participants=1
            )
            logger.info(f"Admin stats updated for UID: {admin_uid}")
        except Exception as e:
            logger.error(f"Failed to update admin stats for UID: {admin_uid} — {str(e)}")

def initialize_user_records(user_id):
    if Reward.objects(user_id=user_id).first() or Referral.objects(user_id=user_id).first():
        return
    user = User.objects(user_id=user_id).first()
    reward = Participants.objects(admin_uid=user.admin_uid, program_id=user.program_id).first()
    signup_reward  =reward.signup_reward
    reward = Reward(user_id=user_id, total_meteors_earned=signup_reward,
                    current_meteors=signup_reward, reward_history=[])
    res = reward.reward_history.append({
        "earned_by_action": "signup",
        "earned_meteors": signup_reward,
        "transaction_type": "credit",
        "referred_on": datetime.datetime.now().strftime("%Y-%m-%d")
    })
    reward.save()
    reward.update(
        set__redeemed_meteors=0,
        push__galaxy_name=["Milky Way Galaxy"],
        push__current_planet=['Planet A']
    )

    Referral(user_id=user_id, all_referrals=[]).save()

    admin = Participants.objects(admin_uid=user.admin_uid, program_id = user.program_id).first()
    if admin:
        admin.update(inc__total_participants=1, inc__signup_earnings=signup_reward)

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
        Errors(name=user.user_id, email=user.email, error_source="Sign Up Form",
               error_type=f" Invalid invitation link {user.user_id}").save()
        logger.info(f"str{e}")
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


        now = datetime.datetime.now()
        now_timestamp = int(now.strftime("%Y%m%d%H%M%S"))

        if now_timestamp > decoded_exp_str:
            return jsonify({"message": "This link has expired"}), 400

        success, msg = reward_referrer_by_tag(tag_id)
        return jsonify({"message": msg}), 200 if success else 400

    except Exception as e:
        Errors(name=user.user_id, email=user.email, error_source="Sign Up Form",
               error_type=f"Expired or Invalid referral link : {user.user_id}, {str(e)}").save()
        return jsonify({"message": "Expired or Invalid referral link"}), 400
