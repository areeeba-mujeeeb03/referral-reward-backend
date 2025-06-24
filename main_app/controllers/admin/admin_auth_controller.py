from flask import request, jsonify
from main_app.models.admin.admin_model import Admin
from main_app.utils.user.helpers import hash_password, check_password,generate_access_token,create_user_session
from main_app.utils.user.error_handling import get_error
import logging
import datetime
# from main_app.models.admin.admin_model import Admin

def admin_register():
    data = request.json

    if Admin.objects(username=data["username"]).first():
        return jsonify({"error": get_error("username_exists")}), 400
    if Admin.objects(email=data["email"]).first():
        return jsonify({"error": get_error("email_exists")}), 400

    hashed_password = hash_password(data["password"])

    user = Admin(
        username=data["username"],
        email=data["email"],
        mobile_number=data["mobile_number"],
        password=hashed_password
    )
    user.save()

    return jsonify({"message": "User registered successfully"}), 200

# //----------------------------------------------------------------------------------------------------------


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def handle_admin_login():

    try:
        logger.info("Starting email login authentication")

        #  Extract and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Login attempt with empty request body")
            return jsonify({"error": get_error("invalid_data")}), 400

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        #  Validate required fields
        if not email or not password:
            return jsonify({
                "error": "Email and password are required",
                "missing_fields": ["email", "password"]
            }), 400

        #  Find user by email
        user = Admin.objects(email=email).first()
        if not user:
            logger.warning(f"Login attempt with unknown email: {email}")
            return jsonify({"error": get_error("user_not_found")}), 404

        #  Check password
        if not check_password(password, user.password):
            logger.warning(f"Incorrect password attempt for: {email}")
            return jsonify({"error": get_error("incorrect_password")}), 400

        #  Generate tokens
        access_token = generate_access_token(user.admin_uid)
        session_id = create_user_session(user.admin_uid)

        #  Update user session info in DB
        user.access_token = access_token
        user.session_id = session_id
        user.last_login = datetime.datetime.now()
        # user.login_count = (user.login_count or 0) + 1  # safe increment

        user.save()

        #  Return success
        logger.info(f"Admin login Successfully: {user.admin_uid}")
        return jsonify({
            "message": "Logged in successfully",
            "access_token": access_token,
            "session_id": session_id,
            "admin_uid": user.admin_uid,
            "username": user.username,
            "email": user.email,
        }), 200

    except Exception as e:
        logger.error(f"Login failed for email with error: {str(e)}")
        return jsonify({"error": get_error("login_failed")}), 500

