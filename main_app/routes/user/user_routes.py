from flask import Blueprint
from main_app.controllers.user.auth_controllers import handle_registration
from main_app.controllers.user.OTP_controllers import generate_and_send_otp, verify_user_otp
from main_app.controllers.user.conversion_controllers import meteors_to_stars, stars_to_currency
from main_app.controllers.user.login_controllers import handle_email_login, logout_user, product_purchase, check_auths, \
    handle_user_authentication
from main_app.controllers.user.forgotpassword_controllers import reset_password,send_verification_code, verify_code
from main_app.controllers.user.landingpage_controllers import my_rewards, my_referrals, my_profile, home_page, \
    fetch_data_from_admin
from main_app.controllers.user.redeem_controllers import redeem
from main_app.controllers.user.referral_controllers import change_invite_link
from main_app.controllers.user.invite import send_whatsapp_invite, send_telegram_invite, send_twitter_invite, \
    send_facebook_invite, send_linkedin_invite
from main_app.controllers.user.rewards_controllers import update_planet_and_galaxy, win_voucher
from main_app.controllers.user.user_profile_controllers import update_profile, submit_msg

user_bp = Blueprint("user_routes", __name__)

# ============

# 1. User Registration

# ============

@user_bp.route("/register", methods = ["POST"])
def register():
    """
    Handle user registration with email and password 
    Accepts: POST request with user registration data
    Returns: Registration response from controller
    """
    return handle_registration()

# ============

# 2. User Registration

# ============

@user_bp.route("/wealthelite.com/invite-link/<tag_id>", methods = ["POST"])
def referral_register(tag_id):
    """
    Handle user registration with email and password
    Accepts: POST request with user registration data
    Returns: Registration response from controller
    """
    return
# =============

# 3. Purchase product

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
 
# 4. User Login Email-Id

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
 
# 5. User Login Mobile Otp with Verify Otp

# =============


@user_bp.route("/login/mobile-send-otp", methods = ["POST"])
def login_send_otp():
    """
    Send OTP to user's mobile number for login
    Accepts: POST request with mobile number
    Returns: OTP send confirmation response
    """
    return generate_and_send_otp()


# =============

# 6. User Login Mobile Otp with Verify Otp

# =============

@user_bp.route("/login/mobile-verify-otp", methods = ["POST"])
def login_verify_otp():
    """
    Verify OTP entered by user for mobile login
    Accepts: POST request with mobile number and OTP
    Returns: Login response with authentication token
    """
    return verify_user_otp()


# ============== 

# 7. User Forgot Password with reset password

# ==============

@user_bp.route("/login/forgot-password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset link to email
    Accepts: POST request with email address
    Returns: Password reset link sent confirmation
    """
    return send_verification_code()

# ==============

# 8. Verify code sent through forgot password API

# ==============

@user_bp.route("/login/verify-code", methods = ["POST"])
def verify_sent_code():

    return verify_code()

# ==============

# 9. reset password

# ==============
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

# 10. Logout

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
# ==============

# 11. User Forgot Password with reset password

# ==============

@user_bp.route("/home", methods = ["POST"])
def home():
    """
    Display user's home/dashboard page
    Accepts: POST request
    Args: user_id (str) - Unique identifier for user
    Returns: User's home page data
    """
    return home_page()

# ==============

# 12. Fetch customized data from admin

# ==============

@user_bp.route('/admin/fetch-custom-data', methods=['POST'])
def fetch_custom_data():
    """
    handles setting default invitation link as special offer link generated from admin side
    Accepts: POST request
    Returns and Saves :
    """
    return fetch_data_from_admin()

# ====================

# 13. User Referrals

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

# 14. User Rewards

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

# 15. User Profile

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

# ==============

# 16. Update profile data

# ==============
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
# ==============

# 17. WhatsAPP

# ==============
@user_bp.route("/send-whatsapp-invite", methods=["POST"])
def send_link_on_whatsapp():
    """
    handles sending invitation link on Whatsapp
    Accepts: POST request
    Redirects : on WhatsApp with pre-typed message
    """
    return send_whatsapp_invite()
# ==============

# 18. Twitter

# ==============
@user_bp.route("/send-twitter-invite", methods=["POST"])
def send_link_on_twitter():
    """
    handles sending invitation link on Twitter
    Accepts: POST request
    Redirects : on Twitter with pre-typed message
    """
    return send_twitter_invite()

# ==============

# 19. Telegram

# ==============

@user_bp.route("/send-telegram-invite", methods=["POST"])
def send_link_on_telegram():
    """
    handles sending invitation link on telegram
    Accepts: POST request
    Redirects : on Telegram with pre-typed message
    """
    return send_telegram_invite()

# ==============

# 20. Facebook

# ==============
@user_bp.route("/send-facebook-invite", methods=["POST"])
def send_link_on_facebook():
    """
    handles sending invitation link on facebook
    Accepts: POST request
    Redirects : on facebook with invite-link NO pre-typed message
    """
    return send_facebook_invite()

# ==============

# 21. LinkedIn

# ==============

@user_bp.route('/send-linkedin-invite', methods = ['POST'])
def send_invite_linkedin():
    """
    handles sending invitation link on LinkedIn
    Accepts: POST request
    Redirects : on LinkedIn with invite-link NO pre-typed message
    """
    return send_linkedin_invite()
# ==============

# 22. Redeem Discount Voucher

# ==============
@user_bp.route("/redeem-offer/<card_type>", methods=["POST"])
def redeem_func(card_type):
    """
    handles sending invitation link on facebook
    Accepts: POST request
    Redirects : on facebook with invite-link NO pre-typed message
    """
    return redeem(card_type)

# ==============

# 23. Help Contact Message

# ==============
@user_bp.route('/contact', methods=['POST'])
def submit():
    """
    handles sending help message on email
    Accepts: POST request
    sends : email to admin
    """
    return submit_msg()

# ==============

# 24. Change Invitation link of user for special offer

# ==============
@user_bp.route('/invite-link', methods=['POST'])
def invite_link():
    """
    handles setting default invitation link as special offer link generated from admin side
    Accepts: POST request
    Returns and Saves :
    """
    return change_invite_link()


# ==============

# 25. Convert Meteors to Stars

# ==============
@user_bp.route('/meteors-to-stars', methods=['POST'])
def meteors_and_stars():
    """
    handles setting default invitation link as special offer link generated from admin side
    Accepts: POST request
    Returns and Saves :
    """
    return meteors_to_stars()

# ==============

# 26. Convert Stars to currency

# ==============
@user_bp.route('/stars-to-currency', methods=['POST'])
def stars_and_currency():
    """
    handles setting default invitation link as special offer link generated from admin side
    Accepts: POST request
    Returns and Saves :
    """
    return stars_to_currency()

# ==============

# 27. update User's planets and galaxy

# ==============
@user_bp.route('/update-user-rewards/<user_id>', methods = ['POST'])
def update(user_id):
    """
    handles setting default invitation link as special offer link generated from admin side
    Accepts: POST request
    Returns and Saves :
    """
    return update_planet_and_galaxy(user_id)


@user_bp.route('/user-logs', methods = ['POST'])
def send_logs():
    return handle_user_authentication()

@user_bp.route('/rewards/<token>/<session>/<user_id>', methods = ['POST'])
def check_user_logs(token, session, user_id):
    return check_auths(token, session, user_id)


