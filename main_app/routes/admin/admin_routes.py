from flask import Blueprint
from main_app.controllers.admin.admin_auth_controller import admin_register, handle_authentication
from main_app.controllers.admin.admin_auth_controller import handle_admin_login
from main_app.controllers.admin.discount_coupons_controllers import create_discount_coupons, update_discount_coupon, \
    delete_discount_coupon
from main_app.controllers.admin.forgotpassword_controllers import forgot_otp_email, verify_otp, reset_password
from main_app.controllers.admin.help_request_controllers import add_faqs, delete_faq, list_contact_messages, update_faqs
from main_app.controllers.admin.profile_controllers import edit_profile_data
from main_app.controllers.admin.product_controllers import add_product, update_product, update_offer, add_offer
from main_app.controllers.admin.prize_controller import add_exciting_prizes, check_eligibility
from main_app.controllers.admin.how_it_work_controller import add_how_it_work, advertisement_card
from main_app.controllers.admin.referral_controllers import generate_invite_link_with_expiry, sharing_app_stats, \
    save_referral_data
from main_app.controllers.admin.rewards_controllers import create_galaxy, remove_milestone, add_new_milestone,set_reward_settings
from main_app.controllers.admin.dashboard_controllers import error_table, dashboard_participants, dashboard_stats, \
    graph_data
from main_app.controllers.admin.email_controller import create_email
from main_app.controllers.admin.notification_controller import create_push_notification, list_push_notifications, update_push_notification, delete_push_notification
from main_app.controllers.admin.perks_controller import create_exclusive_perks, edit_footer
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


# ==================

# 8.  Add offer

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

# ===============

# 11. Check user prize eligibility meteors

# ===============

@admin_bp.route('/admin/check-prize-eligibility', methods=["POST"])
def prize_check_eligibility():
    """
    Checks if a user is eligible for the prize based on certain criteria.
    """
    return check_eligibility()

# ========================

# 12. How It Work

# ========================

@admin_bp.route("/admin/how-it-work", methods = ["POST"])
def admin_how_it_work():
    """
    Add or update 'How It Works' content based on admin_uid.
    """
    return  add_how_it_work()


# ==========================

# 13. Advertisement Card

# ==========================

@admin_bp.route("/admin/advertisement-card", methods = ["POST"])
def admin_advertisement_card():
    """
    Handles the creation of a new advertisement card.
    Add and update advertisement card by admin_uid.
    """
    return advertisement_card()


# =======================================

# 14. Participant table

# =======================================

@admin_bp.route("/admin/dashboard/participant-table", methods =["POST"])
def admin_reward_participant_table():

     return dashboard_participants()

# ===============

# 15. Error

# ===============

@admin_bp.route("/admin/dashboard/error-table", methods = ["POST"])
def admin_error_table():
    return error_table()

# =============

# 16. Dashboard Statistics

# =============

@admin_bp.route('/admin/dashboard/stats', methods = ['POST'])
def fetch_stats():
    return dashboard_stats()
# =============

# 17. Email save

# =============
@admin_bp.route("/admin/send-email", methods = ["POST"])
def admin_send_email():
    """
    handles : admin defining email templates for different e-mails
    """
    return create_email()


# ==============

# 18. Profile update of ADMIN

# ==============

@admin_bp.route("/admin/edit-profile", methods = ["POST"])
def edit_profile():
    """
    Handle profile data updates like username, email

    """
    return edit_profile_data()

# ==============

# 19. Add new FAQ

# ==============

@admin_bp.route('/admin/add-faqs', methods=['POST'])
def add_new_faq():

    return add_faqs()

# ==============

# 20. Update existing FAQ

# ==============


@admin_bp.route('/admin/update-faqs', methods=['PUT'])
def update_faq():

    return update_faqs()

# ==============

# 21. Delete Existing FAQ

# ==============

@admin_bp.route('/admin/delete-faqs', methods=['DELETE'])
def remove_faq():

    return delete_faq()

# ==============

# 22. View messages sent by users

# ==============

@admin_bp.route('/admin/messages', methods=['GET'])
def view_msgs():

    return list_contact_messages()

# ==============

# 23. Generate invitation link with expiry

# ==============

@admin_bp.route('/generate-link', methods = ['POST'])
def generate_link():

    return generate_invite_link_with_expiry()

# ==============

# 24. Generate invitation link with expiry

# ==============

@admin_bp.route('/admin/special-referral-link', methods = ['POST'])
def special_link_referral():

    return save_referral_data()

# ==============

# 25. Sharing platforms

# ==============

@admin_bp.route('/admin/sharing-apps', methods=['POST'])
def sharing_apps():

    return sharing_app_stats()

# ==============

# 26. Referral reward

# ==============

@admin_bp.route('/admin/set-referral-rewards', methods = ['POST'])
def set_referral_rewards():

    return set_reward_settings()

# ==============

# 27. Add New Galaxy

# ==============

@admin_bp.route('/admin/add-new-galaxy', methods = ['POST'])
def add_galaxy():

    return create_galaxy()

# ==============

# 28. Add New Milestone

# ==============

@admin_bp.route('/admin/add-new-milestones', methods = ['POST'])
def add_milestone():

    return add_new_milestone()

# ==================

# 29. Delete milestone

# ===================

@admin_bp.route('/admin/delete-milestone', methods = ['POST'])
def delete_milestone():

    return remove_milestone()

# =======================

# 30. Push Notification

# ========================

@admin_bp.route('/admin/push-notification', methods=['POST'])
def admin_push_notification():
    """
    """
    return create_push_notification()

# ===========================

# 31. List of Notification

# ============================

@admin_bp.route('/admin/table-push-notifications', methods=['POST'])
def admin_list_push_notification():
    """
    """
    return list_push_notifications()

# =================

# 32. Update Notification

# ================

@admin_bp.route('/admin/update-push-notifications/<notification_id>', methods=['PUT'])
def admin_update_push_notification(notification_id):
    """
    """
    return update_push_notification(notification_id)


# =================

# 33. Delete Notification

# ================

@admin_bp.route('/admin/update_push_notifications/<notification_id>', methods=['DELETE'])
def admin_delete_push_notification(notification_id):
    """
    """
    return delete_push_notification(notification_id)

# ==============

# 34. Discount Coupons Generation

# ==============

@admin_bp.route("/admin/create-discount-coupon", methods= ["POST"])
def admin_create_discount_coupons():
    """
    """
    return create_discount_coupons()

# ==============

# 35.  Update Discount Coupons Generation

# ==============

@admin_bp.route("/admin/update-discount-coupon", methods= ["POST"])
def update_coupons():
    """
    """
    return update_discount_coupon()

# ==============

# 36. Discount Coupons Generation

# ==============

@admin_bp.route("/admin/delete-discount-coupon", methods= ["POST"])
def remove_discount_coupons():
    """
    """
    return delete_discount_coupon()

# ===================

# 37. Exclusive Perks

# ====================

@admin_bp.route("/admin/exclusive-perks", methods= ["POST"])
def admin_create_exclusive_perks():
    """
    """
    return create_exclusive_perks()


# ===================

# 38. Footer section

# ==================

@admin_bp.route("/admin/update-footer", methods=["POST"])
def admin_create_footer():

    return edit_footer()

# ===================

# 39. Authentications

# ==================

@admin_bp.route("/admin/auths", methods = ["POST"])
def authentication():
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return handle_authentication()

# =====

# 40.

# =====

@admin_bp.route("/admin/graph-data/<admin_uid>", methods = ["POST"])
def graph(admin_uid):
    """
    Handle password reset using code(otp) from email
    Accepts: POST request with new password and reset
    Returns: Password reset confirmation response
    """
    return graph_data(admin_uid)

# =======

# 41.

# ===========
@admin_bp.route('/admin/special-offer', methods = ['POST'])
def add_special_offer():
    return create_special_offer()