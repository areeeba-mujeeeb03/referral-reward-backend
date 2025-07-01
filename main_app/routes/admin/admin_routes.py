from flask import Blueprint
from main_app.controllers.admin.admin_auth_controller import admin_register
from main_app.controllers.admin.admin_auth_controller import handle_admin_login
from main_app.controllers.admin.forgotpassword_controllers import forgot_otp_email, verify_otp, reset_password
from main_app.controllers.admin.help_request_controllers import list_faqs, add_faq, update_faq, delete_faq,list_contact_messages
from main_app.controllers.admin.help_request_controllers import list_faqs, add_faq, update_faq, delete_faq, \
    list_contact_messages
from main_app.controllers.admin.profile_controllers import edit_profile_data
from main_app.controllers.admin.product_controllers import add_product, update_product, update_offer
from main_app.controllers.admin.prize_controller import add_exciting_prizes
from main_app.controllers.admin.referral_controllers import generate_invite_link_with_expiry
from main_app.controllers.admin.how_it_work_controller import add_how_it_work, advertisement_card
from main_app.controllers.admin.referral_controllers import generate_invite_link_with_expiry

admin_bp = Blueprint("admin_routes", __name__)

#--------------------------------------------------------------------------------

# Admin Register

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


@admin_bp.route("/admin/login/forgot_password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset link to email
    Accepts: POST request with email address
    Returns: Password reset link sent confirmation
    """
    return forgot_otp_email()

# Verify OTP (card)

@admin_bp.route("/admin/forgot/verify_otp", methods = ["POST"])
def forget_otp_verify():
     """
    Handle verify otp request - send to email
    Accepts: POST request with email
    Returns: Password reset confirmation response
     """
     return verify_otp()

# Reset Password

@admin_bp.route("/admin/login/reset_password", methods = ["POST"])
def user_reset_password():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset 
    Returns: Password reset confirmation response
    """
    return reset_password()

# ============================================================================

# Add Products

@admin_bp.route("/admin/add_product", methods = ["POST"])
def admin_add_product():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset 
    Returns: Password reset confirmation response
    """
    return add_product()

# Update Product

@admin_bp.route("/admin/update_offer/<string:uid>", methods = ["PUT"])
def update_add_product(uid):
    """
    Updates an existing product in the database.
    Expects: JSON body with updated product details.
    Returns: Success message or error response.
    """
    return update_product(uid)

# -------------------------------------------------------------------------------------------------

# Add Offers

# @admin_bp.route("/admin/add_offer", methods = ["POST"])
# def admin_add_offer():
#     """
#     Creates a new offer entry.
#     Expects: JSON body with offer details including start and expiry dates.
#     Returns: Success message or error response.
#     """
#     return create_offer()

# Update Offers
@admin_bp.route("/admin/update_offer", methods = ["PUT"])
def admin_update_offer():
    """
    Update offers
    Experts: form-data with offer details including start ans expiry dates.
    Return: Success message or error reponse.
    """
    return update_offer()
# ------------------------------------------------------------------------------------------------

# Exciting Prizes

@admin_bp.route("/admin/prizes", methods = ["POST"])
def admin_exciting_offer():
    """
    Adds exciting prizes.
    Expects: form-data body with prize details such as title, image, terms and conditions
    Returns: Success message or error response.
    """
    return add_exciting_prizes()

# --------------------------------------------------------------------------------------------------

# How It Work

@admin_bp.route("/admin/how_it_work", methods = ["POST"])
def admin_how_it_work():
    """
    
    """
    return  add_how_it_work()



# -----------------------------------------------------------------------------

# Advertisement Card

@admin_bp.route("/admin/advertisement_card", methods = ["POST"])
def admim_advertisement_card():
    """
    
    """
    return advertisement_card()




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

@admin_bp.route('/admin/faqs', methods=['GET'])
def all_faqs():
    return list_faqs()

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
