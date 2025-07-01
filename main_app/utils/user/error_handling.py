import logging
import json
from main_app.utils.user.errors import error_messages

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Error messages loaded successfully from configuration file")
except FileNotFoundError:
    logger.warning("Error configuration file not found, using fallback messages")
    # Fallback error messages if configuration file is missing
    error_messages = {
        "username_exists": "Username already exists",
        "email_exists": "Email already exists",
        "mobile_number_exists" : "Mobile Number already exists",
        "user_not_found": "User not found",
        "incorrect_password": "Incorrect password",
        "Invalid code":"This Referral Code is Invalid",
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