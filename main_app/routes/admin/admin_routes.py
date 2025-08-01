from flask import Blueprint
from main_app.controllers.admin.admin_auth_controller import admin_register, handle_authentication
from main_app.controllers.admin.admin_auth_controller import handle_admin_login
from main_app.controllers.admin.campaign_controllers import create_new_campaign, edit_campaign, update_campaign, \
    delete_campaign, all_products
from main_app.controllers.admin.discount_coupons_controllers import create_discount_coupons, update_discount_coupon, \
    delete_discount_coupon
from main_app.controllers.admin.forgotpassword_controllers import forgot_otp_email, verify_otp, reset_password
from main_app.controllers.admin.help_request_controllers import list_contact_messages
from main_app.controllers.admin.profile_controllers import edit_profile_data
from main_app.controllers.admin.product_controllers import add_product, update_product, delete_product, add_offer,update_offer, delete_offer
from main_app.controllers.admin.prize_controller import add_exciting_prizes, check_eligibility
from main_app.controllers.admin.how_it_work_controller import add_how_it_work, advertisement_card
from main_app.controllers.admin.referral_controllers import generate_invite_link_with_expiry, sharing_app_stats, \
    save_referral_data
from main_app.controllers.admin.rewards_controllers import create_galaxy,set_reward_settings
from main_app.controllers.admin.dashboard_controllers import error_table, dashboard_participants, dashboard_stats, \
    graph_data, dashboard_all_campaigns, reward_history
from main_app.controllers.admin.email_controller import create_email
from main_app.controllers.admin.notification_controller import create_push_notification, list_push_notifications, \
    update_push_notification, delete_push_notification, get_notification
from main_app.controllers.admin.perks_controller import create_exclusive_perks,ExclusivePerks,Perks
from main_app.controllers.admin.special_off_controllers import create_special_offer

admin_bp = Blueprint("admin_routes", __name__)

#--------------------------------------------------------------------------------
# =================

# 1. Admin Register

# ================

@admin_bp.route("/admin/register", methods=["POST"])
def register_admin():
    """
    Handle admin register using email and password
    Accepts: POST request with email and password
    """
    return admin_register()


# ============

# 2. User Login

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

# 3. User Forgot Password with reset password

# ==============

@admin_bp.route("/admin/forgot-password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset code to email
    Accepts: POST request with email address
    """
    return forgot_otp_email()

# ========================

# 4. Verify OTP (card)

# =========================

@admin_bp.route("/admin/verify-otp", methods = ["POST"])
def forget_otp_verify():
     """
    Handle verify otp request - send to email
    Accepts: POST request with email
    Returns: Password reset confirmation response
     """
     return verify_otp()

# =========================

# 5. Reset Password

# =========================

@admin_bp.route("/admin/reset-password", methods = ["POST"])
def user_reset_password():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset 
    Returns: Password reset confirmation response
    """
    return reset_password()

# =============================

# 6. Add Products

# =============================

@admin_bp.route("/admin/add-product", methods = ["POST"])
def admin_add_product():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset 
    Returns: Password reset confirmation response
    """
    return add_product()

# =======================

# 7. Update Product

# ========================

@admin_bp.route("/admin/update-product/<string:product_uid>", methods = ["PUT"])
def update_add_product(product_uid):
    """
    Updates an existing product in the database.
    Expects: JSON body with updated product details.
    Returns: Success message or error response.
    """
    return update_product(product_uid)

# ===========

# Delete product

# ============
@admin_bp.route("/admin/delete-product/<product_uid>", methods=["DELETE"])
def admin_delete_product(product_uid):
    """

    """
    return delete_product(product_uid)

# ==================

#  8. Add offer

# ===================

@admin_bp.route("/admin/add-offer", methods = ["POST"])
def admin_add_offer():
    """
    # Handle password reset using code(otp) from email
    # Accepts: POST request with new password and reset 
    # Returns: Password reset confirmation response
    """
    return add_offer()


# ==========================

# 9. Update Offers

# ==========================

@admin_bp.route("/admin/update-offer", methods = ["PUT"])
def admin_update_offer():
    """
    Update offers
    Experts: JSON with offer details including start ans expiry dates.
    Return: Success message or error reponse.
    """
    return update_offer()


# ================

#  Delete offer

# ================

@admin_bp.route("/admin/delete-offer", methods = ["DELETE"])
def admin_delete_offer():
    """
    Update offers
    Experts: JSON with offer details including start ans expiry dates.
    Return: Success message or error reponse.
    """
    return delete_offer()


# ===========================

# 10. Exciting Prizes

# ===========================

@admin_bp.route("/admin/prizes", methods = ["POST"])
def admin_exciting_prizes():
    """
    Adds exciting prizes.
    Expects: form-data body with prize details such as title, image, term and conditions
    Returns: Success message or error response.
    """
    return add_exciting_prizes()

# =======================================

# 11. Participant table

# =======================================

@admin_bp.route("/admin/dashboard/participant-table", methods =["POST"])
def admin_reward_participant_table():

     return dashboard_participants()

# ===============

# 12. Error

# ===============

@admin_bp.route("/admin/dashboard/error-table", methods = ["POST"])
def admin_error_table():
    return error_table()

# ===============

# 13. Dashboard Graph data

# ===============

@admin_bp.route("/admin/dashboard/graph-data", methods = ["POST"])
def graph():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return graph_data()

# =============

# 14. Dashboard Statistics

# =============

@admin_bp.route('/admin/dashboard/stats', methods = ['POST'])
def fetch_stats():
    return dashboard_stats()

# ===================

# 15. dashboard Reward History

# ==================

@admin_bp.route('/admin/reward-history', methods = ['POST'])
def user_rewards():

    return reward_history()

# =============

# 16. Email save

# =============

@admin_bp.route("/admin/send-email", methods = ["POST"])
def admin_send_email():
    """
    handles : admin defining email templates for different e-mails
    """
    return create_email()

# ==============

# 17. Profile update of ADMIN

# ==============

@admin_bp.route("/admin/edit-profile", methods = ["POST"])
def edit_profile():
    """
    Handle profile data updates like username, email

    """
    return edit_profile_data()

# ==============

# 18. View messages sent by users

# ==============

@admin_bp.route('/admin/messages', methods=['GET'])
def view_msgs():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return list_contact_messages()

# ==============

# 19. Generate invitation link with expiry

# ==============

@admin_bp.route('/generate-link', methods = ['POST'])
def generate_link():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return generate_invite_link_with_expiry()


# =======================

# 20. Push Notification

# ========================

@admin_bp.route('/admin/push-notification', methods=['POST'])
def admin_push_notification():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return create_push_notification()

# ===========================

# 21. List of Notification

# ============================

@admin_bp.route('/admin/table-push-notifications', methods=['POST'])
def admin_list_push_notification():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return list_push_notifications()


# ======

# Get by id

# =======
@admin_bp.route('/admin/get-push-notifications/<notification_id>', methods=['GET'])
def admin_get_push_notification(notification_id):
    """
     Get a single push notification by its ID.
    Expects query parameters:
      - admin_uid
      - mode (as access_token)
      - log_alt (as session_id)
    """
    return get_notification(notification_id)


# =================

# 22. Update Notification

# ================

@admin_bp.route('/admin/update-push-notifications/<notification_id>', methods=['PUT'])
def admin_update_push_notification(notification_id):
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return update_push_notification(notification_id)


# =================

# 23. Delete Notification

# ================

@admin_bp.route('/admin/update_push_notifications/<notification_id>', methods=['DELETE'])
def admin_delete_push_notification(notification_id):
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return delete_push_notification(notification_id)

# ==============

# 25. Discount Coupons Generation

# ==============

@admin_bp.route("/admin/create-discount-coupon", methods= ["POST"])
def admin_create_discount_coupons():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return create_discount_coupons()

# ==============

# 26. Discount Coupons Generation

# ==============

@admin_bp.route("/admin/update-discount-coupon", methods= ["POST"])
def update_coupons():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return update_discount_coupon()

# ==============

# 27. Discount Coupons Generation

# ==============

@admin_bp.route("/admin/delete-discount-coupon", methods= ["POST"])
def remove_discount_coupons():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return delete_discount_coupon()

# ===================

# 28. Exclusive Perks

# ====================

@admin_bp.route("/admin/exclusive-perks", methods= ["POST"])
def admin_create_exclusive_perks():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return create_exclusive_perks()

# ===================

#  29. Authentications

# ==================

@admin_bp.route("/admin/auths", methods = ["POST"])
def authentication():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return handle_authentication()

# ===================

#  30. Authentications

# ==================

@admin_bp.route('/admin/special-offer', methods = ['POST'])
def add_special_offer():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return create_special_offer()

# ===================

# 31. Create Campaign

# ==================

@admin_bp.route('/admin/create-campaign', methods = ['POST'])
def create_campaign():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return create_new_campaign()
# ===================

# 32. Create Campaign

# ==================

@admin_bp.route('/admin/list-all-campaigns', methods=['POST'])
def list_campaign():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return dashboard_all_campaigns()

# ========




@admin_bp.route('/admin/edit-campaign/<program_id>', methods = ['POST'])
def edit_program(program_id):

    return edit_campaign(program_id)

# ===================

# 34. Update Campaign

# ==================

@admin_bp.route('/admin/update-campaign/<program_id>', methods = ['POST'])
def update_program(program_id):

    return update_campaign(program_id)

# ===================

# 35. Delete Campaign

# ==================

@admin_bp.route('/admin/delete-campaign/<program_id>', methods = ['POST'])
def remove_campaign(program_id):

    return delete_campaign(program_id)

# ===================

# 36. Products Data

# ==================

@admin_bp.route('/admin/products/<program_id>', methods = ['POST'])
def view_all(program_id):

    return all_products(program_id)