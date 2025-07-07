from flask import Blueprint
from main_app.controllers.admin.admin_auth_controller import admin_register
from main_app.controllers.admin.admin_auth_controller import handle_admin_login
from main_app.controllers.admin.forgotpassword_controllers import forgot_otp_email, verify_otp, reset_password
from main_app.controllers.admin.help_request_controllers import add_faq, update_faq, delete_faq, list_contact_messages
from main_app.controllers.admin.profile_controllers import edit_profile_data
from main_app.controllers.admin.product_controllers import add_product, update_product, update_offer
from main_app.controllers.admin.prize_controller import add_exciting_prizes, check_eligibility
from main_app.controllers.admin.how_it_work_controller import add_how_it_work, advertisement_card
from main_app.controllers.admin.referral_controllers import generate_invite_link_with_expiry
from main_app.controllers.admin.rewards_controllers import add_new_galaxy, add_new_milestones,remove_milestone
from main_app.controllers.admin.dashboard_controllers import error_table, dashboard_participants
from main_app.controllers.admin.email_controller import create_email

admin_bp = Blueprint("admin_routes", __name__)

#--------------------------------------------------------------------------------
# =================

# Admin Register

# ================

@admin_bp.route("/admin/register", methods=["POST"])
def register_admin():
    """
    Handle admin register using email and password
    Accepts: POST request with email and password
    """
    return admin_register()


# ============

# User Login

# ============


@admin_bp.route("/admin/login", methods=["POST"])
def login_email():
    """
    Handle admin login using email and password
    Accepts: POST request with email and password
    Returns: Login response with authentication token
    """
    return handle_admin_login()

# ==============

# User Forgot Password with reset password

# ==============


@admin_bp.route("/admin/forgot_password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset code to email
    Accepts: POST request with email address
    """
    return forgot_otp_email()

# ========================

# Verify OTP (card)

# =========================

@admin_bp.route("/admin/verify_otp", methods = ["POST"])
def forget_otp_verify():
     """
    Handle verify otp request - send to email
    Accepts: POST request with email
    Returns: Password reset confirmation response
     """
     return verify_otp()

# =========================

# Reset Password

# =========================

@admin_bp.route("/admin/reset_password", methods = ["POST"])
def user_reset_password():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset 
    Returns: Password reset confirmation response
    """
    return reset_password()

# =============================

# Add Products

# =============================

@admin_bp.route("/admin/add_product", methods = ["POST"])
def admin_add_product():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset 
    Returns: Password reset confirmation response
    """
    return add_product()

# =======================

# Update Product

# ========================

@admin_bp.route("/admin/update_product/<string:uid>", methods = ["PUT"])
def update_add_product(uid):
    """
    Updates an existing product in the database.
    Expects: from-data body with updated product details.
    Returns: Success message or error response.
    """
    return update_product(uid)

# ==========================

# Update Offers

# ==========================

@admin_bp.route("/admin/update_offer", methods = ["PUT"])
def admin_update_offer():
    """
    Update offers
    Experts: form-data with offer details including start ans expiry dates.
    Return: Success message or error reponse.
    """
    return update_offer()


# ===========================

# Exciting Prizes

# ===========================

@admin_bp.route("/admin/prizes", methods = ["POST"])
def admin_exciting_offer():
    """
    Adds exciting prizes.
    Expects: form-data body with prize details such as title, image, term and conditions
    Returns: Success message or error response.
    """
    return add_exciting_prizes()


@admin_bp.route('/admin/check_prize_eligibility', methods=["POST"])
def prize_check_eligibility():
    """
    Checks if a user is eligible for the prize based on certain criteria.
    """
    return check_eligibility()



# ========================

# How It Work

# ========================

@admin_bp.route("/admin/how_it_work", methods = ["POST"])
def admin_how_it_work():
    """
    Add or update 'How It Work' content based on admin_uid.
    """
    return  add_how_it_work()


# ==========================

# Advertisement Card

# ==========================

@admin_bp.route("/admin/advertisement_card", methods = ["POST"])
def admin_advertisement_card():
    """
    Handles the creation of a new advertisement card.
    Add and update advertisement card by admin_uid.
    """
    return advertisement_card()


# =======================================

# Participant table

# =======================================

@admin_bp.route("/admin/participant_table", methods =["POST"])
def admin_reward_participant_table():
     return dashboard_participants()



# ===============
# Error
# ===============

@admin_bp.route("/admin/error_table", methods = ["POST"])
def admin_error_table():
    return error_table()


# =============
# Email save
# =============
@admin_bp.route("/admin/send_email", methods = ["POST"])
def admin_send_email():
    return create_email()


# ==============

# Profile update of ADMIN

# ==============

@admin_bp.route("/admin/edit-profile", methods = ["POST"])
def edit_profile():
    """
    Handle profile data updates like username, email

    """
    return edit_profile_data()

# ==============

# View all FAQs

# ==============

# ==============

# Add new FAQ

# ==============

@admin_bp.route('/admin/add-faqs', methods=['POST'])
def add_new_faq():
    return add_faq()

# ==============

# Update existing FAQ

# ==============

@admin_bp.route('/admin/update-faqs/<faq_id>', methods=['PUT'])
def update_faqs(faq_id):
    return update_faq(faq_id)

# ==============

# Delete Existing FAQ

# ==============

@admin_bp.route('/admin/delete-faqs/<faq_id>', methods=['DELETE'])
def remove_faq(faq_id):

    return delete_faq(faq_id)

# ==============

# View messages sent by users

# ==============

@admin_bp.route('/admin/messages', methods=['GET'])
def view_msgs():
    return list_contact_messages()

# ==============

# Generate invitation link with expiry

# ==============

@admin_bp.route('/generate-link', methods = ['POST'])
def generate_link():

    return generate_invite_link_with_expiry()

# ==============

# Generate invitation link with expiry

# ==============

@admin_bp.route('/admin/add-galaxy', methods = ['POST'])
def add_galaxy():

    return add_new_galaxy()

# ==============

# Generate invitation link with expiry

# ==============

@admin_bp.route('/admin/add-new-milestones', methods = ['POST'])
def add_milestone():

    return add_new_milestones()


@admin_bp.route('/admin/delete-milestone', methods = ['POST'])
def delete_milestone():

    return remove_milestone()

# ==============

# Generate invitation link with expiry

# ==============

@admin_bp.route('/admin/sharing_apps', methods=['POST'])
def update_sharing_apps():

    return
