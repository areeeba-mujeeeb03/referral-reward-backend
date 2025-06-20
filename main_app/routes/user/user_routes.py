from flask import Flask, Blueprint
from main_app.controllers.user.auth_controllers import handle_registration, handle_email_login
from main_app.controllers.user.forgotpassword_controllers import reset_password, forgot_password
from main_app.utils.user.otp import generate_and_send_otp, verify_user_otp
from main_app.controllers.user.langingpage_controllers import home_page, my_rewards, my_referrals, my_profile, home_page

user_bp = Blueprint("user_routes", __name__)


# ============

# User Registration

# ============


@user_bp.route("/register", methods = ["POST"])
def register():
    """
    Handle user registration with email and password 
    Accepts: POST request with user registration data
    Returns: Registration response from controller
    """
    return handle_registration()



# =============
 
# User Login Email Id 

# =============


@user_bp.route("/login/email_login", methods = ["POST"])
def login_email():
    """
    Handle user login using email and password
    Accepts: POST request with email and password
    Returns: Login response with authentication token
    """
    return handle_email_login()



# =============
 
# User Login Mobile Otp with Verify Otp

# =============


@user_bp.route("/login/mobile_send_otp", methods = ["POST"])
def login_send_otp():
    """
    Send OTP to user's mobile number for login
    Accepts: POST request with mobile number
    Returns: OTP send confirmation response
    """
    return generate_and_send_otp()

@user_bp.route("/login/mobile_verify_otp", methods = ["POST"])
def login_verify_otp():
    """
    Verify OTP entered by user for mobile login
    Accepts: POST request with mobile number and OTP
    Returns: Login response with authentication token
    """
    return verify_user_otp()


# ============== 

# User Forgot Password with reset password

# ==============


@user_bp.route("login/forgot_password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset link to email
    Accepts: POST request with email address
    Returns: Password reset link sent confirmation
    """
    return forgot_password()

@user_bp.route("/login/reset_password/<token>", methods = ["POST"])
def user_reset_password(token):
    """
    Handle password reset using token from email
    Accepts: POST request with new password and reset token
    Args: token (str) - Password reset token from email
    Returns: Password reset confirmation response
    """
    return reset_password(token)


# ==================== 

# Landing Page APIs 

# ====================


@user_bp.route("/home/<user_id>", methods = ["GET"])
def home(user_id):
    """
    Display user's home/dashboard page
    Accepts: GET request
    Args: user_id (str) - Unique identifier for user
    Returns: User's home page data
    """
    return home_page(user_id)


# ====================

# User Referrals 

# ====================


@user_bp.route("/my-referrals/<user_id>", methods = ["GET"])
def referrals(user_id):
    """
    Display user's referral information and statistics
    Accepts: GET request
    Args: user_id (str) - Unique identifier for user
    Returns: User's referral data and history
    """
    return my_referrals(user_id)

# ====================

# User Rewards

# ====================


@user_bp.route("/my-rewards/<user_id>", methods = ["GET"])
def register(user_id):
    """
    Display user's earned rewards and points
    Accepts: GET request
    Args: user_id (str) - Unique identifier for user
    Returns: User's rewards and points data
    """
    return my_rewards(user_id)


# ====================

# User Profile

# ====================


@user_bp.route("/profile/<user_id>", methods = ["GET"])
def register(user_id):
    """
    Display and manage user profile information
    Accepts: GET request
    Args: user_id (str) - Unique identifier for user
    Returns: User's profile data for viewing/editing
    """
    return my_profile(user_id)

@user_bp.route("/referral/update", methods=["POST"])
def update_referral():
    """
    Update referral information for a user
    Accepts: POST request with referral data
    Returns: Confirmation of referral update
    """
    # Logic to update referral information goes here
    return update_referral()