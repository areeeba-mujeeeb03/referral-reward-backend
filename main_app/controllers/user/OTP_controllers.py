import datetime
import random
import logging
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from flask import request, jsonify

from main_app.controllers.user.login_controllers import SESSION_EXPIRY_MINUTES
from main_app.controllers.user.referral_controllers import update_referral_status_and_reward
from main_app.models.user.user import User
from main_app.utils.user.helpers import generate_access_token, create_user_session

# =============

# CONFIGURATION AND SETUP

# =============

# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

twilio_client = None

# Twilio Configuration - Should be moved to environment variables for security
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '+1 267 813 2952')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC3e746c870fe2af96690590d562902ff9')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '71abde4db0ffb029e4f776693956f182')

# OTP Configuration Constants
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 5
MAX_OTP_ATTEMPTS = 3
OTP_RATE_LIMIT_MINUTES = 1  \

# Development mode flag - set to False in production
DEVELOPMENT_MODE = os.getenv('FLASK_ENV') == 'development'
# DEV_OTP = 123456  # Fixed OTP for development/testing

# Initialize Twilio client with error handling
try:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # Test authentication on startup
    twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
    logger.info("Twilio authentication successful")
except TwilioException as e:
    logger.error(f"Twilio authentication failed: {e}")
    twilio_client = None
except Exception as e:
    logger.error(f"Unexpected error during Twilio initialization: {e}")
    twilio_client = None


# ==============

# OTP GENERATION AND SENDING

# ==============

def generate_and_send_otp():
    """
    Generate and send OTP to user's mobile number for authentication
    
    Process Flow:
    1. Validate request data and mobile number format
    2. Check if user exists and is eligible for OTP
    3. Implement rate limiting to prevent spam
    4. Generate secure OTP
    5. Store OTP with expiry in database
    6. Send OTP via Twilio SMS
    7. Return success/failure response
    
    Expected JSON Request Body:
    {
        "mobile_number": "string (required, format: +1234567890)"
    }
    
    Returns:
        Flask Response: JSON response with OTP sending status
        - Success (200): OTP sent successfully
        - Error (400): Invalid request or rate limit exceeded
        - Error (404): User not found
        - Error (500): SMS service failure
    """
    try:
        logger.info("Starting OTP generation and sending process")
        
        # Step 1: Validate request data
        data = request.get_json()
        if not data:
            logger.warning("OTP request with empty request body")
            return jsonify({
                "success": False, 
                "message": "Invalid request data"
            }), 400
        
        mobile_number = data["mobile_number"].strip()
        
        # Step 2: Validate mobile number format
        if not mobile_number:
            logger.warning("OTP request with missing mobile number")
            return jsonify({
                "success": False, 
                "message": "Mobile number is required"
            }), 400
        
        # Validate mobile number format (basic validation)
        if not _is_valid_mobile_number(mobile_number):
            logger.warning(f"Invalid mobile number format: {mobile_number}")
            return jsonify({
                "success": False, 
                "message": "Invalid mobile number format"
            }), 400
        
        # Step 3: Find user by mobile number
        user = User.objects(mobile_number=mobile_number).first()
        if not user:
            logger.warning(f"OTP request for unregistered mobile: {mobile_number}")
            return jsonify({
                "success": False, 
                "message": "User not registered with this mobile number"
            }), 404

        # Step 4: Check rate limiting
        rate_limit_check = _check_otp_rate_limit(user)
        if rate_limit_check:
            return rate_limit_check
            # Rate limiting

        if not DEVELOPMENT_MODE:
            rate_limit_response = _check_otp_rate_limit(user)
            if rate_limit_response:
                return rate_limit_response

        # Step 5: Generate OTP
        otp = _generate_otp()
        otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=OTP_EXPIRY_MINUTES)

        logger.info(f"Generated OTP for user: {user.user_id}")

        # Step 6: Store OTP in database
        user.update(
            otp=otp,
            otp_expires_at=otp_expiry,
        )
        
        # Step 7: Send OTP via SMS
        if DEVELOPMENT_MODE:
            logger.info(f"Development mode: Using fixed OTP {otp}")
            # In development, use fixed OTP for testing
            user.update(otp=otp)
            return jsonify({
                "success": True,
                "message": "OTP sent successfully (Development Mode)",
                "dev_otp": otp,  # Only for development
                "expires_in_minutes": OTP_EXPIRY_MINUTES
            }), 200
        else:
            # Production: Send actual SMS
            sms_result = _send_otp_sms(mobile_number, otp)
            if not sms_result:
                logger.error(f"Failed to send OTP SMS to: {mobile_number}")
                return jsonify({
                    "success": False,
                    "message": "Failed to send OTP. Please try again."
                }), 500
        
        # Step 8: Return success response
        logger.info(f"OTP sent successfully to: {mobile_number}")
        return jsonify({
            "success": True,
            "message": "OTP sent successfully",
            "expires_in_minutes": OTP_EXPIRY_MINUTES,
            "max_attempts": MAX_OTP_ATTEMPTS
        }), 200
        
    except Exception as e:
        logger.error(f"Error in OTP generation: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error occurred"
        }), 500


def _generate_otp():
    """
    Generate a cryptographically secure OTP
    
    Returns:
        int: Random OTP of specified length
    """
    min_value = 10**(OTP_LENGTH-1)  # Minimum value (e.g., 100000 for 6 digits)
    max_value = 10**OTP_LENGTH - 1  # Maximum value (e.g., 999999 for 6 digits)
    
    # Use cryptographically secure random number generation
    return random.SystemRandom().randint(min_value, max_value)


def _is_valid_mobile_number(mobile_number):
    """
    Validate mobile number format
    
    Args:
        mobile_number (str): Mobile number to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    import re
    
    # Basic validation for international format (+1234567890)
    # Adjust pattern based on your requirements
    pattern = r'^\+[1-9]\d{1,14}$'  # E.164 format
    
    if re.match(pattern, mobile_number):
        return True
    
    # Alternative: Allow 10-digit numbers without country code
    if re.match(r'^\d{10}$', mobile_number):
        return True
    
    return False


def _check_otp_rate_limit(user):
    """
    Check if user has exceeded OTP request rate limit
    
    Args:
        user (User): User object to check
        
    Returns:
        Flask Response or None: Error response if rate limited, None if allowed
    """
    if hasattr(user, 'otp_requested_at') and user.otp_requested_at:
        time_since_last_request = datetime.datetime.now() - user.otp_requested_at
        if time_since_last_request.total_seconds() < (OTP_RATE_LIMIT_MINUTES * 60):
            remaining_seconds = (OTP_RATE_LIMIT_MINUTES * 60) - time_since_last_request.total_seconds()
            logger.warning(f"Rate limit exceeded for user: {user.user_id}")
            return jsonify({
                "success": False,
                "message": f"Please wait {int(remaining_seconds)} seconds before requesting another OTP",
                "retry_after_seconds": int(remaining_seconds)
            }), 429
    
    return None


def _send_otp_sms(mobile_number, otp):
    """
    Send OTP via Twilio SMS service
    
    Args:
        mobile_number (str): Recipient's mobile number
        otp (int): OTP to send
        
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """

    if not twilio_client:
        logger.error("Twilio client not initialized")
        return False
    
    try:
        message_body = f"Your verification code is: {otp}. This code will expire in {OTP_EXPIRY_MINUTES} minutes. Do not share this code with anyone."
        
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=f"+91{mobile_number}"
        )
        
        logger.info(f"SMS sent successfully. Message SID: {message.sid}")
        print("a")
        return True
        
    except TwilioException as e:
        logger.error(f"Twilio error sending SMS: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending SMS: {e}")
        return False


# ===========

# OTP VERIFICATION

# ==========
def verify_user_otp():
    """
    Verify OTP entered by user for authentication
    
    Process Flow:
    1. Validate request data and required fields
    2. Find user by mobile number
    3. Check if OTP exists and hasn't expired
    4. Verify OTP matches stored value
    5. Check attempt limits
    6. Clear OTP from database on success
    7. Return verification result
    
    Expected JSON Request Body:
    {
        "mobile_number": "string (required)",
        "otp_input": "integer (required, 6-digit OTP)"
    }
    
    Returns:
        Flask Response: JSON response with verification status
        - Success (200): OTP verified successfully
        - Error (400): Invalid OTP, expired, or validation errors
        - Error (404): User not found
        - Error (429): Too many attempts
    """
    try:
        logger.info("Starting OTP verification process")
        
        # Step 1: Validate request data
        data = request.get_json()
        if not data:
            logger.warning("OTP verification with empty request body")
            return jsonify({
                "success": False,
                "message": "Invalid request data"
            }), 400
        
        mobile_number = data.get("mobile_number", "").strip()
        otp_input = data.get("otp_input")

        # Step 2: Validate required fields
        if not mobile_number or otp_input is None:
            logger.warning("OTP verification with missing required fields")
            return jsonify({
                "success": False,
                "message": "Mobile number and OTP are required",
                "missing_fields": [
                    field for field in ["mobile_number", "otp_input"]
                    if not data.get(field)
                ]
            }), 400
        
        # Step 3: Validate OTP input format
        try:
            otp_input = int(otp_input)
        except (ValueError, TypeError):
            logger.warning(f"Invalid OTP format provided: {otp_input}")
            return jsonify({
                "success": False,
                "message": "OTP must be a valid number"
            }), 400
        
        # Step 4: Find user by mobile number
        user = User.objects(mobile_number=mobile_number).first()
        if not user:
            logger.warning(f"OTP verification for unknown mobile: {mobile_number}")
            return jsonify({
                "success": False,
                "message": "User not found"
            }), 404
        is_member = user.is_member

        if not is_member == True:
            return "Need to purchase before logging in!"
        
        # Step 5: Check if OTP exists
        if not hasattr(user, 'otp') or user.otp is None:
            logger.warning(f"No OTP found for user: {user.user_id}")
            return jsonify({
                "success": False,
                "message": "No OTP found. Please request a new OTP."
            }), 400
        
        # Step 6: Check OTP expiry
        if not hasattr(user, 'otp_expires_at') or user.otp_expires_at is None:
            logger.warning(f"No OTP expiry found for user: {user.user_id}")
            return jsonify({
                "success": False,
                "message": "OTP has expired. Please request a new OTP."
            }), 400
        
        if datetime.datetime.now() > user.otp_expires_at:
            logger.warning(f"Expired OTP verification attempt for user: {user.user_id}")
            # Clear expired OTP
            user.update(unset__otp=1, unset__otp_expires_at=1)
            return jsonify({
                "success": False,
                "message": "OTP has expired. Please request a new OTP."
            }), 400
        
        # Step 7: Check attempt limits
        # attempt_check = _check_otp_attempts(user)
        # if attempt_check:
        #     return attempt_check
        
        # Step 8: Verify OTP
        if otp_input != user.otp:
            logger.warning(f"Invalid OTP attempt for user: {user.user_id}")
            # Increment attempt counter
            current_attempts = getattr(user, 'otp_attempts', 0) + 1
            # user.update(otp_attempts=current_attempts)
            
            remaining_attempts = MAX_OTP_ATTEMPTS - current_attempts
            if remaining_attempts > 0:
                return jsonify({
                    "success": False,
                    "message": "Invalid OTP",
                    "remaining_attempts": remaining_attempts
                }), 400
            else:
                # Clear OTP after max attempts
                user.update(unset__otp=1, unset__otp_expires_at=1, unset__otp_attempts=1)
                return jsonify({
                    "success": False,
                    "message": "Maximum OTP attempts exceeded. Please request a new OTP."
                }), 429

        # referee = User.objects(mobile_number = mobile_number).first()
        # referrer = referee.referred_by
        # if referrer:
        #     referee_id = referee.user_id
        #     referrer_id = User.objects(user_id = referrer).first()
        #     update_referral_status_and_reward(referrer_id, referee_id)

        access_token = generate_access_token(user.user_id)
        session_id = create_user_session(user.user_id)
        expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)

        user.access_token = access_token
        user.session_id = session_id
        user.expiry_time = expiry_time
        user.save()
        # Step 9: OTP is valid - clear it from database
        user.update(
            unset__otp=1,
            unset__otp_expires_at=1,
            set__access_token = user.access_token,
            set__session_id = user.session_id,
            set__expiry_time = user.expiry_time
        )

        # Step 10: Return success response
        logger.info(f"OTP verified successfully for user: {user.user_id}")
        return jsonify({
            "success": True,
            "message": "OTP verified successfully",
            "user_id": user.user_id,
            "verified_at": datetime.datetime.now().isoformat(),
            "mode" : user.access_token,
            "log_alt" : user.session_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in OTP verification: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Internal server error occurred"
        }), 500


# def _check_otp_attempts(user):
#     """
#     Check if user has exceeded maximum OTP verification attempts
#
#     Args:
#         user (User): User object to check
#
#     Returns:
#         Flask Response or None: Error response if limit exceeded, None if allowed
#     """
#     current_attempts = getattr(user, 'otp_attempts', 0)
#     if current_attempts >= MAX_OTP_ATTEMPTS:
#         logger.warning(f"Max OTP attempts exceeded for user: {user.user_id}")
#         # Clear OTP to force new request
#         user.update(unset__otp=1, unset__otp_expires_at=1, unset__otp_attempts=1)
#         return jsonify({
#             "success": False,
#             "message": "Maximum OTP attempts exceeded. Please request a new OTP."
#         }), 429
#
    return None


# ==============

# UTILITY FUNCTIONS

# ==============

def cleanup_expired_otp():
    """
    Utility function to clean up expired OTPs from database
    This should be run periodically as a background job
    
    Returns:
        int: Number of expired OTPs cleaned up
    """
    try:
        current_time = datetime.datetime.now()
        expired_users = User.objects(otp_expires_at__lt=current_time)
        
        count = 0
        for user in expired_users:
            user.update(
                unset__otp=1,
                unset__otp_expires_at=1,
                unset__otp_attempts=1,
                unset__otp_requested_at=1
            )
            count += 1
        
        if count > 0:
            logger.info(f"Cleaned up {count} expired OTPs")
        
        return count
        
    except Exception as e:
        logger.error(f"Error cleaning up expired OTPs: {e}")
        return 0


def get_otp_status(mobile_number):
    """
    Get current OTP status for a mobile number
    
    Args:
        mobile_number (str): Mobile number to check
        
    Returns:
        dict: OTP status information
    """
    try:
        user = User.objects(mobile_number=mobile_number).first()
        if not user:
            return {"exists": False}
        
        has_active_otp = (
            hasattr(user, 'otp') and user.otp and
            hasattr(user, 'otp_expires_at') and user.otp_expires_at and
            datetime.datetime.now() < user.otp_expires_at
        )
        
        status = {
            "exists": True,
            "has_active_otp": has_active_otp,
            "attempts": getattr(user, 'otp_attempts', 0),
            "max_attempts": MAX_OTP_ATTEMPTS
        }
        
        if has_active_otp:
            remaining_time = user.otp_expires_at - datetime.datetime.now()
            status["expires_in_seconds"] = int(remaining_time.total_seconds())
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting OTP status: {e}")
        return {"error": "Failed to get OTP status"}