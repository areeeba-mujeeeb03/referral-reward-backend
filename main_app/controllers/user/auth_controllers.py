import logging
import re
import datetime
from flask import request, jsonify

from main_app.controllers.user.rewards_controllers import update_planet_and_galaxy
from main_app.controllers.user.user_profile_controllers import update_app_stats
from main_app.models.admin.error_model import Errors
from main_app.models.admin.links import ReferralReward
from main_app.models.user.user import User
from main_app.controllers.user.referral_controllers import (process_referral_code_and_reward, initialize_user_records,
                                                            process_tag_id_and_reward ,process_referrer_by_tag_id,
                                                            update_referral_status_and_reward)
from main_app.utils.user.helpers import hash_password
from main_app.utils.user.error_handling import get_error

# ================

# Configuration and setup

# ===============

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================

# User Registration Controllers

# ==================

def handle_registration():
    logger.info("Starting user registration process")

    data = request.get_json()
    if not data:
        logger.warning("Registration attempt with empty request body")
        return jsonify({"error": get_error("invalid_data")}), 400

    required_fields = ["username", "email", "mobile_number", "password", "confirm_password"]
    validation_result = _validate_required_fields(data, required_fields)
    if validation_result:
        return validation_result
    
    if data['email'] != data['email'].lower():
            return jsonify({"message": "Email must be in lowercase only"}), 400

    if validate_email_format(data["email"]):
        return validate_email_format(data["email"])

    if not re.match(r'^\d{10}$', str(data["mobile_number"])):
        return jsonify({"error": "Mobile must be 10 digits"}), 400

    if data["password"] != data["confirm_password"]:
        return jsonify({"error": "Password and Confirm Password do not match"}), 400

    if validate_password_strength(data["password"]):
        return validate_password_strength(data["password"])
    username = data["username"]
    conflict_check = _check_user_conflicts(username, data["email"], data['mobile_number'])
    if conflict_check:
        return conflict_check

    hashed_password = hash_password(data["password"])
    user = User(
        username=username,
        email=data["email"],
        mobile_number=data["mobile_number"],
        admin_uid="AD_UID_2",
        password=hashed_password,
        created_at=datetime.datetime.now(),
        is_active=True
    )

    # Save user early if referral via tag_id
    tag_id = data.get("tag_id")
    if tag_id:
        inviter = User.objects(tag_id=data["tag_id"]).first()
        if not inviter:
            return jsonify({"error": "Invalid referral link"}), 400
        user.save()
        process_referrer_by_tag_id(tag_id, user.user_id, user.username)

    referral_code = data.get("referral_code")
    if referral_code:
        inviter = User.objects(invitation_code=referral_code).first()
        if not inviter:
            return jsonify({"error": "Invalid referral code"}), 400
        user.save()
        update_referral_status_and_reward(inviter.user_id, user.user_id)
        process_referrer_by_tag_id(inviter.tag_id, user.user_id, user.username)

    if not user.pk:
        user.save()
    app = data.get("accepted_via")

    rates = ReferralReward.objects(admin_uid=user.admin_uid).first() or {}
    rewards_info = {
        "signup_reward": getattr(rates, "signup_reward", 0),
        "login_reward": getattr(rates, "login_reward", 0)
    }

    if app:
        update_app_stats(app, user)
    initialize_user_records(user.user_id)

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.user_id,
        "registration_date": user.created_at.isoformat(),
        "rewards": [rewards_info]
    }), 200


# ==================

# User Registration Validation Utilities

# ==================

def _validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present and non-empty
    
    Args:
        data (dict): Request data dictionary
        required_fields (list): List of required field names
        
    Returns:
        Flask Response or None: Error response if validation fails, None if valid
    """
    for field in required_fields:
        if not data.get(field) or not str(data.get(field)).strip():
            logger.warning(f"Missing or empty required field: {field}")
            return jsonify({
                "error": f"Missing required field: {field}",
                "field": field
            }), 400
    return None

# ==================

# Email Format Validation Utility

# ==================

def validate_email_format(email):
    """
    Validate email address format using regex pattern
    
    Args:
        email (str): Email address to validate
        
    Returns:
        Flask Response or None: Error response if invalid, None if valid
    """
    import re
    

    email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    # email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        logger.warning(f"Invalid email format provided: {email}")
        return jsonify({"error": "Invalid email format"}), 400
    return None


# ==================

# Password Strength Validation Utility

# ==================
def validate_password_strength(password):
    """
    Validate password meets minimum security requirements
    
    Password Requirements:
    - Minimum 8 characters length
    - At least one uppercase letter
    - At least one lowercase letter  
    - At least one numeric digit
    
    Args:
        password (str): Password to validate
        
    Returns:
        Flask Response or None: Error response if weak, None if strong
    """

    if len(password) < 8:
        print("start")
        return jsonify({"error": "Password must be at least 8 characters long"}), 400

    if not any(c.isupper() for c in password):
        return jsonify({"error": "Password must contain at least one uppercase letter"}), 400
    
    if not any(c.islower() for c in password):
        return jsonify({"error": "Password must contain at least one lowercase letter"}), 400
    
    if not any(c.isdigit() for c in password):
        return jsonify({"error": "Password must contain at least one number"}), 400

    return None


# ==================

# Check for existing username or email conflicts

# =================

def _check_user_conflicts(username, email, mobile_number):
    """
    Check if username or email already exists in the database
    
    Args:
        username (str): Username to check
        email (str): Email address to check
        
    Returns:
        Flask Response or None: Error response if conflict exists, None if available
    """
    # Check for existing username
    existing_username = User.objects(username=username.strip('').lower()).first()
    if existing_username:
        Errors(username = username, email = existing_username.email,
               error_source = "Sign Up Form", error_type = get_error("registration_failed")).save()
        logger.warning(f"Registration attempt with existing username: {username}")
        return jsonify({"error": get_error("username_exists")}), 400
    
    # Check for existing email
    existing_email = User.objects(email=email).first()
    if existing_email:
        Errors(username = existing_email.username, email = email,
               error_source = "Sign Up Form", error_type = get_error("registration_failed")).save()
        logger.warning(f"Registration attempt with existing email: {email}")
        return jsonify({"error": get_error("email_exists")}), 400

    existing_mobile_num = User.objects(mobile_number=mobile_number).first()
    if existing_mobile_num:
        Errors(username = existing_mobile_num.username, email = existing_mobile_num.email,
               error_source = "Sign Up Form", error_type = get_error("registration_failed")).save()
        logger.warning(f"Registration attempt with existing mobile number: {mobile_number}")
        return jsonify({"error": "Mobile number already exists"}), 400
    return None


# ==================

# User Session Validation Utility

# ==================


def validate_session_token(user, access_token, session_id):
    """
    Validate if access token is valid, not expired, and tied to the correct session.

    Returns:
        tuple: (is_valid: bool, user: User or None, error_message: str or None, status_code: int)
    """
    try:
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if user.access_token != access_token:
            return ({"success" :False,
                     "message" : "Invalid access token"}), 401

        if user.session_id != session_id:
            return ({"success" : False,
                     "message" : "Session mismatch or invalid session"}), 403

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return ({"success"  : False,
                         "message" : "Access token has expired"}), 401
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        Errors(username=user.username, email=user.email, error_source="Reset Password",
              error_type=get_error("code validation failed")).save()
        return jsonify({"success" : False,
                        "message" : "Token validation failed"}), 500