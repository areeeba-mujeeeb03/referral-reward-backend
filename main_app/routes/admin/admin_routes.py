from flask import Flask, Blueprint
from main_app.controllers.admin.admin_auth_controller import handle_admin_login
from main_app.controllers.admin.forgotpassword_controllers import forgot_password, reset_password
from main_app.controllers.admin.profile_controllers import edit_profile_data


admin_bp = Blueprint("admin_routes", __name__)


# ============

# User Login

# ============


@admin_bp.route("/login", methods=["POST"])
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


@admin_bp.route("login/forgot_password", methods = ["POST"])
def user_forgot_password():
    """
    Handle forgot password request - send reset link to email
    Accepts: POST request with email address
    Returns: Password reset link sent confirmation
    """
    return forgot_password()

@admin_bp.route("/login/reset_password/<token>", methods = ["POST"])
def user_reset_password(token):
    """
    Handle password reset using token from email
    Accepts: POST request with new password and reset token
    Args: token (str) - Password reset token from email
    Returns: Password reset confirmation response
    """
    return reset_password(token)

@admin_bp.route("edit/<admin_uid>", methods = ["POST"])
def edit_profile(admin_uid):
    """
    Handle profile data updates like username, email

    """
    return edit_profile_data(admin_uid)