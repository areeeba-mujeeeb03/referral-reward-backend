import json
import datetime
import logging

from flask import request, jsonify, session
from main_app.models.user.user import User
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral
from main_app.utils.user.helpers import (
    hash_password, 
    check_password, 
    generate_access_token, 
    create_user_session
)
from main_app.utils.user.otp import generate_and_send_otp, verify_user_otp


# ================

# Configuration and setup

# ===============

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Referral reward points configuration
REFERRAL_REWARD_POINTS = 400
SESSION_EXPIRY_MINUTES = 30


# Load error messages from configuration file
try:
    with open('main_app/utils/user/errors.json', 'r') as f:
        error_messages = json.load(f)
    logger.info("Error messages loaded successfully from configuration file")
except FileNotFoundError:
    logger.warning("Error configuration file not found, using fallback messages")
    # Fallback error messages if configuration file is missing
    error_messages = {
        "username_exists": "Username already exists",
        "email_exists": "Email already exists", 
        "user_not_found": "User not found",
        "incorrect_password": "Incorrect password",
        "invalid_data": "Invalid or missing data",
        "registration_failed": "Registration failed",
        "login_failed": "Login failed",
        "missing_required_field": "Required field is missing",
        "server_error": "Internal server error occurred"
    }
except json.JSONDecodeError:
    logger.error("Error configuration file contains invalid JSON")
    error_messages = {}


# ==================

# Error Handling Utilities

# ==================

def get_error(error_key):
    """
    Retrieve error message by key with fallback mechanism
    
    Args:
        error_key (str): Key identifier for the error message
        
    Returns:
        str: Corresponding error message or generic fallback
    """
    return error_messages.get(error_key, "An unexpected error occurred")



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
        if not data:
            logger.warning("Registration attempt with empty request body")
            return jsonify({"error": get_error("invalid_data")}), 400
        
        # Step 2: Validate all required fields are present
        required_fields = ["username", "email", "mobile_number", "password"]
        validation_result = _validate_required_fields(data, required_fields)
        if validation_result:
            return validation_result
        
        # Step 3: Additional field-specific validation
        email_validation = _validate_email_format(data["email"])
        if email_validation:
            return email_validation
            
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
        logger.info(f"User account created successfully with ID: {user.user_id}")
        
        # Step 6: Process referral code if provided
        referral_code = data.get("referral_code")
        if referral_code:
            logger.info(f"Processing referral code: {referral_code}")
            _process_referral_code(referral_code, user.user_id)
        
        # Step 7: Initialize user's reward and referral tracking records
        _initialize_user_records(user.user_id)
        
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
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
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

# Referral Code Processing Utility

# ==================
def _process_referral_code(referral_code, new_user_id):
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
        # Find the user who owns this referral code
        referring_user = User.objects(invitation_code=referral_code).first()
        if not referring_user:
            logger.warning(f"Invalid referral code provided: {referral_code}")
            return  # Skip processing for invalid codes
        
        logger.info(f"Processing referral for user: {referring_user.user_id}")
        current_time = datetime.datetime.now()
        
        # Update referrer's referral statistics
        _update_referral_statistics(referring_user.user_id, new_user_id, current_time)
        
        # Update referrer's reward points
        _update_referral_rewards(referring_user.user_id, current_time)
        
        logger.info(f"Referral processing completed for code: {referral_code}")
        
    except Exception as e:
        logger.error(f"Error processing referral code {referral_code}: {str(e)}")
        # Don't fail registration if referral processing fails



def _update_referral_statistics(referrer_user_id, new_user_id, timestamp):
    """
    Update referrer's referral statistics and tracking records
    
    Args:
        referrer_user_id (str): ID of the user who referred
        new_user_id (str): ID of the newly registered user
        timestamp (datetime): Time of referral processing
    """
    referral_record = Referral.objects(user_id=referrer_user_id).first()
    if referral_record:
        # Update referral counters
        referral_record.total_referrals += 1
        referral_record.referral_earning += REFERRAL_REWARD_POINTS
        referral_record.pending_referrals += 1
        
        # Add detailed referral record
        referral_record.all_referrals.append({
            "user_id": new_user_id,
            "status": "pending",
            "earned_points": REFERRAL_REWARD_POINTS,
            "referred_on": timestamp,
            "referral_type": "registration"
        })
        
        referral_record.save()
        logger.info(f"Updated referral statistics for user: {referrer_user_id}")


def _update_referral_rewards(referrer_user_id, timestamp):
    """
    Update referrer's reward points and transaction history
    
    Args:
        referrer_user_id (str): ID of the user who referred
        timestamp (datetime): Time of reward processing
    """
    reward_record = Reward.objects(user_id=referrer_user_id).first()
    if reward_record:
        # Add reward points
        reward_record.total_meteors += REFERRAL_REWARD_POINTS
        
        # Record reward transaction
        reward_record.reward_history.append({
            "earned_by_action": "referral",
            "earned_points": REFERRAL_REWARD_POINTS,
            "referral_status": "pending",
            "referred_on": timestamp,
            "transaction_type": "credit"
        })
        
        reward_record.save()
        logger.info(f"Updated reward points for user: {referrer_user_id}")


def _initialize_user_records(user_id):
    """
    Initialize empty reward and referral tracking records for new user
    
    Args:
        user_id (str): ID of the newly registered user
    """
    try:
        # Create initial reward record with zero balance
        user_reward = Reward(
            user_id=user_id,
            total_meteors=0,
            reward_history=[],
            created_at=datetime.datetime.now()
        )
        user_reward.save()
        
        # Create initial referral record with zero stats
        user_referral = Referral(
            user_id=user_id,
            total_referrals=0,
            referral_earning=0,
            pending_referrals=0,
            all_referrals=[],
            created_at=datetime.datetime.now()
        )
        user_referral.save()
        
        logger.info(f"Initialized reward and referral records for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to initialize user records for {user_id}: {str(e)}")
        # This is non-critical, so we don't fail the registration




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
    try:
        logger.info("Starting email login authentication")
        
        # Step 1: Extract and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Login attempt with empty request body")
            return jsonify({"error": get_error("invalid_data")}), 400
        
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        # Step 2: Validate required authentication fields
        if not email or not password:
            logger.warning("Login attempt with missing email or password")
            return jsonify({
                "error": "Email and password are required",
                "missing_fields": [
                    field for field in ["email", "password"] 
                    if not data.get(field)
                ]
            }), 400
        
        # Step 3: Find user account by email
        user = User.objects(email=email).first()
        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return jsonify({"error": get_error("user_not_found")}), 404
        
        # Step 4: Check if user account is active
        if hasattr(user, 'is_active') and not user.is_active:
            logger.warning(f"Login attempt with inactive account: {email}")
            return jsonify({"error": "Account is deactivated"}), 403
        
        # Step 5: Verify password against stored hash
        if not check_password(password, user.password):
            logger.warning(f"Failed login attempt for email: {email}")
            return jsonify({"error": get_error("incorrect_password")}), 400
        
        # Step 6: Generate authentication tokens
        access_token = generate_access_token(user.user_id)
        session_id = create_user_session(user.user_id)
        
        # Step 7: Calculate token expiry time
        expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)
        
        # Step 8: Update user's session information
        user.update(
            access_token=access_token,
            session_id=session_id,
            expiry_time=expiry_time,
            last_login=datetime.datetime.now(),
            login_count=getattr(user, 'login_count', 0) + 1  # Track login frequency
        )
        
        # Step 9: Return successful authentication response
        logger.info(f"Successful login for user: {user.user_id}")
        return jsonify({
            "message": "Logged in successfully",
            "access_token": access_token,
            "session_id": session_id,
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "expires_at": expiry_time.isoformat(),
            "expires_in_seconds": SESSION_EXPIRY_MINUTES * 60
        }), 200
        
    except Exception as e:
        logger.error(f"Login failed with error: {str(e)}")
        return jsonify({"error": get_error("login_failed")}), 500


# ==================

# User Session Validation Utility

# ==================


def validate_session_token(access_token):
    """
    Validate if access token is still valid and not expired
    
    Args:
        access_token (str): Access token to validate
        
    Returns:
        tuple: (is_valid: bool, user: User or None, error_message: str or None)
    """
    try:
        if not access_token:
            return False, None, "Access token is required"
        
        user = User.objects(access_token=access_token).first()
        if not user:
            return False, None, "Invalid access token"
        
        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return False, None, "Access token has expired"
        
        return True, user, None
        
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        return False, None, "Token validation failed"



# ==================

# User Logout Controller

# ==================

def logout_user(user_id):
    """
    Handle user logout by invalidating tokens and session
    
    Args:
        user_id (str): ID of user to logout
        
    Returns:
        bool: True if logout successful, False otherwise
    """
    try:
        user = User.objects(user_id=user_id).first()
        if user:
            user.update(
                access_token=None,
                session_id=None,
                expiry_time=None,
                last_logout=datetime.datetime.now()
            )
            logger.info(f"User logged out successfully: {user_id}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Logout failed for user {user_id}: {str(e)}")
        return False