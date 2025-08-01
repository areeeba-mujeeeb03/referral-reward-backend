import logging
import re
import datetime
from flask import request, jsonify
from main_app.controllers.user.user_profile_controllers import update_app_stats
from main_app.models.admin.campaign_model import Campaign
from main_app.models.admin.error_model import Errors
from main_app.models.admin.links import ReferralReward
from main_app.models.admin.participants_model import Participants
from main_app.models.user.user import User
from main_app.controllers.user.referral_controllers import (initialize_user_records ,process_referrer_by_tag_id,
                                                            update_referral_status_and_reward)
from main_app.utils.user.helpers import hash_password
from main_app.utils.user.error_handling import get_error
from main_app.utils.user.string_encoding import generate_encoded_string

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
    # try :
    if not data:
        logger.warning("Registration attempt with empty request body")
        return jsonify({"error": get_error("invalid_data")}), 400

    required_fields = ['name', 'email', 'mobile_number', 'password', 'confirm_password']

    validation_result = _validate_required_fields(data, required_fields)
    if validation_result:
        return validation_result

    if validate_email_format(data['email']):
        return validate_email_format(data['email'])

    if not re.match(r'^\d{10}$', str(data["mobile_number"])):
        return jsonify({"error": "Mobile must be 10 digits"}), 400

    if data['password'] != data['confirm_password']:
        return jsonify({"error": "Password and Confirm Password do not match"}), 400

    if validate_password_strength(data['password']):
        return validate_password_strength(data['password'])
    conflict_check = _check_user_conflicts(data['email'], data['mobile_number'])
    if conflict_check:
        return conflict_check

    url = data.get('url')
    find_url = Campaign.objects(base_url = url).first()
    if not find_url:
        return jsonify({"error" : "URL not found", "success" : False}),400

    hashed_password = hash_password(data['password'])
    user = User(
        name = data['name'],
        email=data['email'],
        mobile_number=data['mobile_number'],
        program_id = find_url.program_id,
        password=hashed_password,
        created_at=datetime.datetime.now(),
        admin_uid = find_url.admin_uid
    )
    user.save()

    # Save user early if referral via tag_id
    tag_id = data.get("tag_id")
    if tag_id:
        inviter = User.objects(tag_id=data["tag_id"]).first()
        if not inviter:
            return jsonify({"error": "Invalid referral link"}), 400
        user.save()
        process_referrer_by_tag_id(tag_id, user.user_id, user.name)

    referral_code = data.get('referral_code')
    if referral_code:
        inviter = User.objects(invitation_code=referral_code).first()
        if not inviter:
            return jsonify({"error": "Invalid referral code"}), 400
        user.save()
        update_referral_status_and_reward(inviter.user_id, user.user_id)
        process_referrer_by_tag_id(inviter.tag_id, user.user_id, user.name)

    # if not user.pk:
    #     user.save()

    app = data.get("accepted_via")
    if app:
        user.update(
            set__joined_via = app
        )
        update_app_stats(app, user)

    rates = ReferralReward.objects(admin_uid=user.admin_uid, program_id = user.program_id).first() or {}
    rewards_info = Participants.objects(admin_uid=user.admin_uid, program_id = user.program_id).first()

    rewards = {
        "signup_reward" : rewards_info.signup_reward,
        "login_reward": rewards_info.login_reward

    }

    initialize_user_records(user.user_id)

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.user_id,
        "registration_date": user.created_at.isoformat(),
        "rewards": [rewards]
    }), 200

    # except Exception as e:
    #     logger.info(f"Registration failed as {str(e)}")
    #     return jsonify({"error" : "Registration Failed", "success" : False}), 400


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

    # missing = [field for field in required_fields if not data.get(field)]
    # if missing:
    #     return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

    for field in required_fields:
        # missing = [field for field in field if not data.get(field)]
        # if missing:
        #     return jsonify({"error": f"Missing required fields: {missing}"}), 400
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
    

    # email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
    # email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


    if not re.match(email_pattern, email):
        logger.warning(f"Invalid email format provided: {email}")
        return jsonify({"error": "Invalid email format", "success" : False}), 400

    if not email == email.lower():
        return jsonify({"error": "Email must be in lower case", "success" : False})
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

# Check for existing mobile number or email conflicts

# =================

def _check_user_conflicts(email, mobile_number):
    """
    Check if mobile_number or email already exists in the database
    
    Args:
        email (str): Email address to check
        
    Returns:
        Flask Response or None: Error response if conflict exists, None if available
    """
    
    # Check for existing email
    existing_email = User.objects(email=email).first()
    if not existing_email:
        return None
    if existing_email:
        print(existing_email)
        Errors(admin_uid = existing_email.admin_uid, program_id = existing_email.program_id, 
               name = existing_email.name, email = email,
               error_source = "Sign Up Form", error_type = get_error("registration_failed")).save()
        logger.warning(f"Registration attempt with existing email: {email}")
        return jsonify({"error": get_error("email_exists")}), 400

    existing_mobile_num = User.objects(mobile_number = mobile_number).first()
    if not existing_mobile_num:
        return None
    if existing_mobile_num:
        Errors(admin_uid = existing_mobile_num.admin_uid, program_id = existing_mobile_num.program_id, 
               name = existing_mobile_num.name, email = existing_mobile_num.email,
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
            return jsonify({"error": "Missing token or session", "success": False}), 400

        if user.access_token != access_token:
            return ({"success" :False,
                     "error" : "Invalid access token"}), 401

        if user.session_id != session_id:
            return ({"success" : False,
                     "error" : "Session mismatch or invalid session"}), 403

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return ({"success"  : False,
                         "error" : "Access token has expired"}), 401

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        Errors(admin_uid = user.admin_uid, program_id = user.program_id, name=user.name, email=user.email, error_source="Reset Password",
              error_type=get_error("code validation failed")).save()
        return jsonify({"success" : False,
                        "error" : "Token validation failed"}), 500