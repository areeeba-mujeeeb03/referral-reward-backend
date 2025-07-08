from itertools import product
from flask import Blueprint, jsonify
from pymongo import DESCENDING

from main_app.controllers.user.auth_controllers import handle_registration
from main_app.controllers.user.OTP_controllers import generate_and_send_otp, verify_user_otp
from main_app.controllers.user.login_controllers import handle_email_login, logout_user, product_purchase
from main_app.controllers.user.forgotpassword_controllers import reset_password,send_verification_code, verify_code
from main_app.controllers.user.landingpage_controllers import my_rewards, my_referrals, my_profile, home_page, \
    fetch_data_from_admin
from main_app.controllers.user.referral_controllers import change_invite_link
from main_app.controllers.user.invite import send_whatsapp_invite, send_telegram_invite, send_twitter_invite, send_facebook_invite
from main_app.controllers.user.user_profile_controllers import update_profile, help_faq, submit_msg
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.user.reward import Reward

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

@user_bp.route("/wealthelite.com/invite-link/<tag_id>", methods = ["POST"])
def referral_register(tag_id):
    """
    Handle user registration with email and password
    Accepts: POST request with user registration data
    Returns: Registration response from controller
    """
    return
# =============

# Purchase product

# =============

@user_bp.route("/purchase", methods=["POST"])
def purchase():

    """
    handles the visit on wealth elite product purchase
    Accepts: POST request
    Returns: Confirmation of purchase
    """

    return product_purchase()

# =============
 
# User Login Email Id 

# =============


@user_bp.route("/login/email-login", methods = ["POST"])
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


@user_bp.route("/login/mobile-send-otp", methods = ["POST"])
def login_send_otp():
    """
    Send OTP to user's mobile number for login
    Accepts: POST request with mobile number
    Returns: OTP send confirmation response
    """
    return generate_and_send_otp()

@user_bp.route("/login/mobile-verify-otp", methods = ["POST"])
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


@user_bp.route("/login/forgot-password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset link to email
    Accepts: POST request with email address
    Returns: Password reset link sent confirmation
    """
    return send_verification_code()

@user_bp.route("/login/verify-code", methods = ["POST"])
def verify_sent_code():

    return verify_code()

@user_bp.route("/login/reset-password", methods = ["POST"])
def user_reset_password():
    """
    Handle password reset using token from email
    Accepts: POST request with new password and reset token
    Args: token (str) - Password reset token from email
    Returns: Password reset confirmation response
    """
    return reset_password()

# ====================

# Logout

# ====================

@user_bp.route("/logout", methods=["POST"])
def logout():
    """
    unsets access token, session_id and expiry_time
    Accepts: POST request with user_id
    Returns: Confirmation of logout
    """
    # Logic to update referral information goes here
    return logout_user()

# ==================== 

# Landing Page APIs 

# ====================

@user_bp.route("/home", methods = ["POST"])
def home():
    """
    Display user's home/dashboard page
    Accepts: POST request
    Args: user_id (str) - Unique identifier for user
    Returns: User's home page data
    """
    return home_page()

# ====================

# User Referrals 

# ====================


@user_bp.route("/my-referrals", methods = ["POST"])
def referrals():
    """
    Display user's referral information and statistics
    Accepts: POST request
    Args: user_id (str) - Unique identifier for user
    Returns: User's referral data and history
    """
    return my_referrals()

# ====================

# User Rewards

# ====================


@user_bp.route("/my-rewards", methods = ["POST"])
def rewards():
    """
    Display user's earned rewards and points
    Accepts: POST request
    Args: user_id (str) - Unique identifier for user
    Returns: User's rewards and points data
    """
    return my_rewards()


# ====================

# User Profile

# ====================


@user_bp.route("/profile", methods = ["POST"])
def profile():
    """
    Display and manage user profile information
    Accepts: POST request
     (str) - Unique identifier for user
    Returns: User's profile data for viewing/editing
    """
    return my_profile()

@user_bp.route("/update-profile", methods = ["POST"])
def update_user_profile():
    """
    User's profile data for viewing/editing
    Accepts: POST request
     (str) - Unique identifier for user
    Returns: Updated user info
    """
    return update_profile()

# ====================

# Invitation Links

# ====================


@user_bp.route("/send-whatsapp-invite", methods=["POST"])
def send_link_on_whatsapp():
    """
    handles sending invitation link on Whatsapp
    Accepts: POST request
    Redirects : on WhatsApp with pre-typed message
    """
    return send_whatsapp_invite()

@user_bp.route("/send-twitter-invite", methods=["POST"])
def send_link_on_twitter():
    """
    handles sending invitation link on Twitter
    Accepts: POST request
    Redirects : on Twitter with pre-typed message
    """
    return send_twitter_invite()

@user_bp.route("/send-telegram-invite", methods=["POST"])
def send_link_on_telegram():
    """
    handles sending invitation link on telegram
    Accepts: POST request
    Redirects : on Telegram with pre-typed message
    """
    return send_telegram_invite()

@user_bp.route("/send-facebook-invite", methods=["POST"])
def send_link_on_facebook():
    """
    handles sending invitation link on facebook
    Accepts: POST request
    Redirects : on facebook with invite-link NO pre-typed message
    """
    return send_facebook_invite()

@user_bp.route("/help-request", methods=["POST"])
def help_request():
    """
    handles sending invitation link on facebook
    Accepts: POST request
    Redirects : on facebook with invite-link NO pre-typed message
    """
    return help_faq()

@user_bp.route("/redeem-voucher", methods=["POST"])
def redeem_voucher():
    """
    handles sending invitation link on facebook
    Accepts: POST request
    Redirects : on facebook with invite-link NO pre-typed message
    """
    return

@user_bp.route('/contact', methods=['POST'])
def submit():
    """
    handles sending help message on email
    Accepts: POST request
    sends : email to admin
    """
    return submit_msg()


@user_bp.route('/invite-link', methods=['POST'])
def invite_link():
    """
    handles setting default invitation link as special offer link generated from admin side
    Accepts: POST request
    Returns and Saves :
    """
    return change_invite_link()

@user_bp.route('/admin/fetch_custom_data', methods=['POST'])
def fetch_custom_data():

    return fetch_data_from_admin()

@user_bp.route('/<user_id>' , methods = ['POST'])
def update_planet_and_galaxy(user_id):
    reward = Reward.objects(user_id = user_id).first()
    all_galaxies = reward.galaxy_name
    current_galaxy = all_galaxies[-1]
    find_galaxy = Galaxy.objects(galaxy_name = current_galaxy).first()

    if not find_galaxy:
        return jsonify({"message" : "This galaxy does not exist"})

    target = find_galaxy.total_meteors_required
    if reward.total_meteors <= target:
        check = Galaxy.objects(galaxy_name = current_galaxy).first()
        milestones = find_galaxy.all_milestones
        for milestone in milestones:
            required_meteors = milestones['required_to_unlock', 'milestone_name']
            points = required_meteors['meteors_required_to_unlock']
            user_milestone = reward.current_planet
            find_milestone = check.all_milestones.objects(milestone_name__nin = user_milestone)

            if find_milestone and reward.total_meteors >= points:
                user_milestone.append = find_milestone['milestone_name']
                return jsonify({"message" : "new planet unlocked"})

    if reward.total_meteors >= target:
        next_planet = Galaxy.objects(galaxy_name__nin = all_galaxies).first()
        reward.update(
            push__galaxy_name = next_planet.galaxy_name
        )
        print(reward.galaxy_name)
        return jsonify({"message" : "New Galaxy Unlocked", "success" : True})


