import datetime
import logging
import re
from flask import request, jsonify, session
from main_app.models.user.user import User
from main_app.controllers.user.referral_controllers import (process_referral_code_and_reward, initialize_user_records,
                                                            process_tag_id_and_reward)
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
    """
    Handle complete user registration process including validation,
    referral processing, and initial account setup
    
    Process Flow:
    1. Validate request data and required fields
    2. Check for existing username/email conflicts
    3. Hash password securely
    4. Create new user account
    5. Process referral code if provided
    6. Initialize user reward and referral records
    7. Return success response with user details
    
    Expected JSON Request Body:
    {
        "username": "string (required)",
        "email": "string (required)", 
        "mobile_number": "string (required)",
        "password": "string (required)",
        "referral_code": "string (optional)"
    }
    
    Returns:
        Flask Response: JSON response with registration status
        - Success (200): User details and confirmation
        - Error (400): Validation errors or conflicts
        - Error (500): Server-side processing errors
    """
    try:
        logger.info("Starting user registration process")
        
        # Step 1: Extract and validate request data
        data = request.get_json()
        print(data)
        if not data:
            logger.warning("Registration attempt with empty request body")
            return jsonify({"error": get_error("invalid_data")}), 400
        
        # Step 2: Validate all required fields are present
        required_fields = ["username", "email", "mobile_number", "password", "confirm_password"]
        validation_result = _validate_required_fields(data, required_fields)
        if validation_result:
            return validation_result
        # Step 3: Additional field-specific validation
        email_validation = _validate_email_format(data["email"])
        if email_validation:
            return email_validation
            

        if not re.match(r'^\d{10}$',str(data["mobile_number"])):
            return jsonify({"error": "Mobile must be 10 digits"}), 400

        if data["password"] != data["confirm_password"]:
            return jsonify({"error": "Password and Confirm Password do not match"}), 400


        password_validation = _validate_password_strength(data["password"])
        if password_validation:
            return password_validation
        
        # Step 4: Check for existing user conflicts
        conflict_check = _check_user_conflicts(data["username"], data["email"])
        if conflict_check:
            return conflict_check
        
        # Step 5: Create new user with secure password
        hashed_password = hash_password(data["password"])
        logger.info(f"Creating new user account for: {data['username']}")

        user = User(
            username=data["username"],
            email=data["email"],
            mobile_number=data["mobile_number"],
            password=hashed_password,
            created_at=datetime.datetime.now(),  # Track account creation time
            is_active=True  # Set account as active by default
        )

        user.save()
        print(user.user_id)
        # Step 6: Process referral code if provided
        try:
            referral_code = data.get("referral_code")
            referrer_id = User.objects(invitation_code = referral_code).first()
            if referral_code:
                logger.info(f"Processing referral code: {referral_code}")
                user.update(
                    set__referred_by = referrer_id.user_id
                )
                process_referral_code_and_reward(referral_code, user.user_id)
        except Exception as e:
            return jsonify({"error" : get_error("failed_to_update")})
        print(user)
        logger.info(f"User account created successfully with ID: {user.user_id}")

        # Step 7: Initialize user's reward and referral tracking records
        initialize_user_records(user.user_id)
        
        # Step 8: Return successful registration response
        logger.info(f"User registration completed successfully for: {user.user_id}")
        return jsonify({
            "message": "User registered successfully",
            "user_id": user.user_id,
            "tag_id": user.tag_id,
            "username": user.username,
            "email": user.email,
            "registration_date": user.created_at.isoformat() if hasattr(user, 'created_at') else None
        }), 200
        
    except Exception as e:
        logger.error(f"Registration failed with error: {str(e)}")
        return jsonify({"error": get_error("registration_failed")}), 500

def handle_registration_with_tag_id(tag_id):
    try:
        response, response["user_id"] = handle_registration()

        if response.status_code != 200 or not response["user_id"]:
            return response

        process_tag_id_and_reward(tag_id, response["user_id"])
        return response
    except Exception as e:
        logger.error(f"Registration failed with error: {str(e)}")
        return jsonify({"error": get_error("registration_failed")}), 500

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

def _validate_email_format(email):
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
def _validate_password_strength(password):
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

def _check_user_conflicts(username, email):
    """
    Check if username or email already exists in the database
    
    Args:
        username (str): Username to check
        email (str): Email address to check
        
    Returns:
        Flask Response or None: Error response if conflict exists, None if available
    """
    # Check for existing username
    existing_username = User.objects(username=username).first()
    if existing_username:
        logger.warning(f"Registration attempt with existing username: {username}")
        return jsonify({"error": get_error("username_exists")}), 400
    
    # Check for existing email
    existing_email = User.objects(email=email).first()
    if existing_email:
        logger.warning(f"Registration attempt with existing email: {email}")
        return jsonify({"error": get_error("email_exists")}), 400
    
    return None


# ==================

# User Session Validation Utility

# ==================


import datetime


import datetime

def validate_session_token(user_id, access_token, session_id):
    """
    Validate if access token is valid, not expired, and tied to the correct session.

    Returns:
        tuple: (is_valid: bool, user: User or None, error_message: str or None, status_code: int)
    """
    try:
        if not user_id:
            return ({"success" : False,
                     "message" : "User ID is required"}), 400

        if not access_token:
            return ({"success" : False,
                    "message" : "Access token is required"}), 400

        if not session_id:
            return ({"success" : False,
                     "message" : "Session ID is required"}), 400

        user = User.objects(user_id=user_id).first()

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

        return jsonify({"success" : True}), 200

    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return jsonify({"success" : False,
                        "message" : "Token validation failed"}), 500

