import datetime
import logging
from main_app.models.admin.links import Link
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


# ==================

# Referral Code Processing Utility

# ==================
def process_referral_code_and_reward(referral_code, new_user_id):
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
    try:
        valid_code = User.objects(invitation_code = referral_code).first()
        referrer_id = str(valid_code.user_id)
        if valid_code:
            referrer = Referral.objects(user_id = referrer_id).first()
            referrer.update(
                push__all_referrals={
                    "user_id": new_user_id,
                    "referral_status": "Pending",
                    "date" : datetime.datetime.now(),
                    "earned_meteors" : PENDING_REFERRAL_REWARD_POINTS

                },
                inc__total_referrals = 1,
                inc__pending_referrals=1,
                inc__referral_earning = PENDING_REFERRAL_REWARD_POINTS

            )
            reward_record = Reward.objects(user_id=referrer_id).first()
            if reward_record:
                # Add reward points
                reward_record.total_meteors += PENDING_REFERRAL_REWARD_POINTS
                reward_record.reward_history.append({
                    "earned_by_action": "referral",
                    "earned_meteors": PENDING_REFERRAL_REWARD_POINTS,
                    "referred_to" : new_user_id,
                    "referral_status": "pending",
                    "referred_on": datetime.datetime.now(),
                    "transaction_type": "credit"
                })

                reward_record.save()

    except Exception as e:
        logger.error(f"Failed to initialize user records.: {str(e)}")

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
    try:
        valid_user = User.objects(tag_id = tag_id).first()
        referrer = Referral.objects(user_id = valid_user.user_id).first()
        referrer.save()
        new_user = User.objects(user_id = new_user_id).first()
        if new_user:
            new_user.update(
                set__referred_by = valid_user.user_id
            )
        referrer.update(
            push__all_referrals={
                "user_id": new_user_id,
                "referral_status": "Pending",
                "date" : datetime.datetime.now(),
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
                "referred_to" : new_user_id,
                "referral_status": "pending",
                "referred_on": datetime.datetime.now(),
                "transaction_type": "credit"
            })

            reward_record.save()

    except Exception as e:
        logger.error(f"Failed to initialize user records.: {str(e)}")


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
    referral_record.save()
    logger.info(f"Referral stats updated for referrer: {referrer_id}")

    # Now update the referrer’s reward
    reward_record = Reward.objects(user_id=referrer_id).first()
    if not reward_record:
        logger.warning(f"No reward record found for user: {referrer_id}")
        return

    # No double-crediting
    already_rewarded = any(
        entry.get("earned_by_action") == "referral" and
        entry.get("referral_status") == "Completed" and
        entry.get("referred_user_id") == user_id
        for entry in reward_record.reward_history
    )

    if already_rewarded:
        logger.info(f"Reward already credited for referral of user {user_id}")
        return

    # Append a new reward entry
    reward_record.total_meteors += SUCCESS_REFERRAL_REWARD_POINTS
    reward_record.reward_history.append({
        "earned_by_action": "referral",
        "earned_meteors": SUCCESS_REFERRAL_REWARD_POINTS,
        "referral_status": "Completed",
        "referred_user_id": user_id,
        "referred_on": datetime.datetime.utcnow(),
        "transaction_type": "credit"
    })
    reward_record.save()
    logger.info(f"Reward added for referrer: {referrer_id}")



def initialize_user_records(user_id):
    """
    Initialize empty reward and referral tracking records for new user

    Args:
        user_id (str): ID of the newly registered user
    """
    try:
        user = Reward.objects(user_id = user_id).first()
        if user :
            return "The rewards for this user is already initialized"
        user_reward = Reward(
            user_id=user_id,
            total_meteors=0,
            reward_history=[]
        )
        user_reward.save()

        user_referral = Referral(
            user_id=user_id,
            total_referrals=0,
            referral_earning=0,
            pending_referrals=0,
            all_referrals=[]
        )
        user_referral.save()

        logger.info(f"Initialized reward and referral records for user: {user_id}")

    except Exception as e:
        logger.error(f"Failed to initialize user records for {user_id}: {str(e)}")
        # This is non-critical, so we don't fail the registration

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
    user_id = data.get("user_id")
    link = data.get("link")

    user = User.objects(user_id=user_id).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    tag_id = user.tag_id

    default_invitation_link = user.invitation_link

    link = Link.objects(invitation_link = link).first()
    print(Link)
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
    return jsonify({"success" : True, "message" : "Invitation Link generated"})


# ==================

# Handles rewards for special offer

# ==================

def reward_referrer_by_tag(tag_id: str):
    user = User.objects(tag_id=tag_id).first()
    if not user:
        return False, "Invalid tag ID"

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

    reward_record.total_meteors += SUCCESS_REFERRAL_REWARD_POINTS
    reward_record.reward_history.append({
        "earned_by_action": "link_visit",
        "earned_meteors": SUCCESS_REFERRAL_REWARD_POINTS,
        "referral_status": "Visited",
        "referred_user_id": "anonymous",
        "referred_on": datetime.datetime.utcnow(),
        "transaction_type": "credit"
    })
    reward_record.save()
    return True, "Referral reward granted successfully"

def handle_invitation_visit(encoded_gen_str, tag_id, encoded_exp_str):
    """Args:
        tag_id (str): ID of the user referring
        encoded_gen_str : generation time of link
        encoded_exp_str : expiry time of link
    """
    try:
        decoded_gen_str = decode_timestamp(encoded_gen_str)
        decoded_exp_str = decode_timestamp(encoded_exp_str)
    except Exception as e:
        return jsonify({"message": "Invalid referral link"}), 400

    now = datetime.datetime.utcnow()
    now_timestamp = int(now.strftime("%Y%m%d%H%M%S"))

    if now_timestamp > decoded_exp_str:
        return jsonify({"message": "This link has expired"}), 400

    success, msg = reward_referrer_by_tag(tag_id)
    return jsonify({"message": msg}), 200 if success else 400