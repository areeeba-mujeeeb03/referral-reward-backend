import logging
from flask import jsonify, request
from main_app.controllers.user.rewards_controllers import update_planet_and_galaxy
from main_app.controllers.user.user_profile_controllers import update_app_stats
from main_app.models.admin.error_model import Errors
from main_app.models.admin.participants_model import Participants
from main_app.models.user.reward import Reward
from main_app.utils.user.helpers import (check_password,generate_access_token,create_user_session)
from main_app.controllers.user.referral_controllers import update_referral_status_and_reward
from main_app.utils.user.error_handling import get_error
import datetime
from main_app.models.user.user import User
from main_app.utils.user.string_encoding import generate_encoded_string

# Referral reward points configuration
REFERRAL_REWARD_POINTS = 400
SESSION_EXPIRY_MINUTES = 30

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def product_purchase():
    data = request.get_json()
    user_id = data.get("user_id")

    user = User.objects(user_id = user_id).first()
    if not user :
        return jsonify({"message": "User not Found", "success" : False}), 404

    user.update(
        set__is_member = True
    )
    return jsonify({"message" : "Purchase Done", "success" : True}), 200
# ==================

# User Authentication Controllers

# ==================
def handle_email_login():
    """
    Handle user authentication using email and password credentials

    Authentication Process:
    1. Validate request data and required fields
    2. Find user account by email address
    3. Verify password against stored hash
    4. Generate access token and session
    5. Update user's session information
    6. Return authentication tokens

    Expected JSON Request Body:
    {
        "email": "string (required)",
        "password": "string (required)"
    }

    Returns:
        Flask Response: JSON response with authentication status
        - Success (200): Access token, session ID, and user info
        - Error (400): Invalid credentials or missing data
        - Error (404): User account not found
        - Error (500): Server-side authentication errors
    """
    data = request.get_json()
    logger.info("Starting email login authentication")

    # Step 1: Extract and validate request data

    if not data:
        logger.warning("Login attempt with empty request body")
        return jsonify({"error": get_error("invalid_data")}), 400

    email = data.get("email")
    password = data.get("password")

    # Step 2: Validate required fields
    if email and password:
        missing_fields = [field for field in ["email", "password"] if not data.get(field)]
        if missing_fields:
            logger.warning(f"Missing fields during login: {missing_fields}")
            return jsonify({
                "error": "Email and password are required",
                "missing_fields": missing_fields,
                "success" : False
            }), 400

    # Step 3: Find user by email
    user = User.objects(email=email).first()
    # if not user:
    #     user_name = User.objects(username=email).first()
    #     if not user_name:
    #         logger.warning(f"Login attempt with unknown username: {email}")
    #         return jsonify({"error": get_error("user_not_found")}), 404
    #
    #     if user_name.username != email:
    #         return jsonify({"message" :  "Invalid email"})
    #     is_member = user_name.is_member
    #
    #     if not is_member == True:
    #         return jsonify({"success" : False, "message" : "Need to purchase before logging in!"}), 400
    #
    #     # Step 4: Check if account is active
    #     if hasattr(user_name, "is_active") and not user_name.is_active:
    #         logger.warning(f"Inactive account login attempt: {email}")
    #         return jsonify({"error": "Account is deactivated"}), 403
    #
    #     if not user_name.password.startswith("$2"):
    #         logger.warning("Invalid or corrupt password hash")
    #         return jsonify({"success": False, "message": "Something went wrong. Please reset your password."}), 400
    #     # Step 5: Verify password
    #     if not check_password(password, user_name.password):
    #         Errors(username=user_name.username, email=email,admin_uid = user.admin_uid,program_id = user.program_id,
    #                error_source="Login Form", error_type= f"Incorrect password attempt for: {email}").save()
    #         logger.warning(f"Incorrect password attempt for: {email}")
    #         return jsonify({"error": get_error("incorrect_password")}), 400
    #     # Step 6: Generate tokens
    #     access_token = generate_access_token(user_name.user_id)
    #     session_id = create_user_session(user_name.user_id)
    #     expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)
    #
    #     # Step 7: Update referral status (if referred)
    #     referred_by = user_name['referred_by']
    #
    #     if referred_by:
    #         referrer_obj = User.objects(user_id=referred_by).first()
    #         referrer = referrer_obj.user_id
    #         update_referral_status_and_reward(referrer, user_name.user_id)
    #
    #     # Step 8: Update user session info in DB
    #     user_name.access_token = access_token
    #     user_name.session_id = session_id
    #     user_name.expiry_time = expiry_time
    #     user_name.joining_status = "Completed"
    #     user_name.last_login = datetime.datetime.now()
    #     user_name.login_count = (user_name.login_count or 0) + 1  # safe increment
    #
    #     user_name.save()
    #     reward = Reward.objects(user_id = user_name.user_id).first()
    #     reward_earn = Participants.objects(admin_uid=user.admin_uid, program_id=user.program_id).first()
    #     login_reward = reward_earn.login_reward
    #     date = datetime.datetime.now()
    #     for referral in reward.reward_history:
    #         if not referral.get("earned_by_action") == "Log In":
    #             reward.reward_history.append({
    #                 "earned_by_action": "Log In",
    #                 "earned_meteors": login_reward,
    #                 "referred_to": user_name.username,
    #                 "referral_status": "pending",
    #                 "referred_on": date.strftime('%d-%m-%y'),
    #                 "transaction_type": "credit"
    #             })
    #
    #     # Step 9: Return success
    #     logger.info(f"Successful login for user: {user_name.user_id}")
    #     return jsonify({
    #         "message": "Logged in successfully",
    #         "mode": access_token,
    #         "log_alt": session_id,
    #         "user_id": user_name.user_id
    #     }), 200

    if user:
        if user.email != email:
            return jsonify({"message": "Invalid email"})
        is_member = user.is_member

        if not is_member == True:
            return jsonify({"success": False, "message": "Need to purchase before logging in!"}), 400

        # Step 4: Check if account is active

        if hasattr(user, "is_active") and not user.is_active:
            logger.warning(f"Inactive account login attempt: {email}")
            return jsonify({"error": "Account is deactivated"}), 403

        if not user.password.startswith("$2"):
            logger.warning("Invalid or corrupt password hash")
            return jsonify({"success": False, "message": "Something went wrong. Please reset your password."}), 400
        # Step 5: Verify password
        if not check_password(password, user.password):
            Errors(name=user.name, email=email,
                   error_source="Login Form", error_type=f"Incorrect password attempt for: {email}").save()
            logger.warning(f"Incorrect password attempt for: {email}")
            return jsonify({"error": get_error("incorrect_password")}), 400

        # Step 6: Generate tokens
        access_token = generate_access_token(user.user_id)
        session_id = create_user_session(user.user_id)
        expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)

        # Step 7: Update referral status (if referred)
        referred_by = user['referred_by']

        if referred_by:
            referrer_obj = User.objects(user_id=referred_by).first()
            referrer = referrer_obj.user_id
            update_referral_status_and_reward(referrer, user.user_id)

        # Step 8: Update user session info in DB
        user.access_token = access_token
        user.session_id = session_id
        user.expiry_time = expiry_time
        user.joining_status = "Completed"
        user.last_login = datetime.datetime.now()
        user.login_count = (user.login_count or 0) + 1  # safe increment

        user.save()
        reward = Reward.objects(user_id = user.user_id).first()
        reward_earn= Participants.objects(admin_uid=user.admin_uid, program_id=user.program_id).first()
        login_reward = reward_earn.login_reward
        date = datetime.datetime.now()
        for referral in reward.reward_history:
            if not referral.get("earned_by_action") == "Log In":
                reward.reward_history.append({
                    "earned_by_action": "Log In",
                    "earned_meteors": login_reward,
                    "referred_to": user.name,
                    "referral_status": "pending",
                    "referred_on": date.strftime('%d-%m-%y'),
                    "transaction_type": "credit"
                })
        app_name = user.joined_via
        update_app_stats(app_name, user)

        # Step 9: Return success
        logger.info(f"Successful login for user: {user.user_id}")
        return jsonify({
            "message": "Logged in successfully",
            "mode": access_token,
            "log_alt": session_id,
            "user_id": user.user_id
        }), 200

    Errors(admin_uid=user.admin_uid, program_id=user.program_id, name=user.name, email=user.email,
           error_source="Reset Password",
           error_type=get_error("code validation failed")).save()
    return jsonify({"error": get_error("login_failed")}), 500

# ==================

# User Logout Controller

# ==================

def logout_user():
    """
    Handle user logout by invalidating tokens and session

    Args:
        user_id (str): ID of user to logout

    Returns:
        bool: True if logout successful, False otherwise
    """
    data = request.json
    user_id = data.get("user_id")
    user = User.objects(user_id=user_id).first()
    try:
        if user:
            user.update(
                access_token=None,
                session_id=None,
                expiry_time=None,
            )
            logger.info(f"User logged out successfully: {user_id}")

            return jsonify({"message": "Logged out successfully", "success" : True}), 200

    except Exception as e:
        logger.error(f"Logout failed for user {user_id}: {str(e)}")
        Errors(name=user.name, email=user.email, error_type=get_error("logout_failed"),
               error_source="Logout form").save()
        return jsonify({"message": "Something went wrong", "success" : False}), 400

def handle_user_authentication():
    data = request.get_json()
    user_id = data.get("user_id")

    existing = User.objects(user_id = user_id).first()

    if not existing:
        logger.warning("User not found")
        return jsonify({"message": get_error("user_not_found")}), 404

    #  Generate tokens
    access_token = generate_access_token(existing.admin_uid)
    session_id = create_user_session(existing.admin_uid)
    expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)

    #  Update user session info in DB
    existing.access_token = access_token
    existing.session_id = session_id
    existing.expiry_time = expiry_time
    existing.last_login = datetime.datetime.now()
    existing.save()

    info = {"access_token": access_token,
            "session_id": session_id,
            "user_id" : user_id}

    fields_to_encode = ["access_token", "session_id", "user_id"]

    res = generate_encoded_string(info, fields_to_encode)
    return jsonify({"logs" : res,
                    "success" : True}),200

def check_auths(token, session, user_id):
    data = request.get_json()
    return jsonify({"message" : "Successfully", "success" : True})