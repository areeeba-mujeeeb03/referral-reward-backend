from flask import request, jsonify
from main_app.models.admin.admin_model import Admin
from main_app.utils.user.helpers import hash_password, check_password,generate_access_token,create_user_session
from main_app.utils.user.error_handling import get_error
import logging
import datetime
import re
from main_app.controllers.user.auth_controllers import _validate_password_strength, _validate_email_format

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def is_valid_email(email):
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{3}$'
#     return re.match(pattern, email) is not None

#------- Register 

def admin_register():
 try:
      logger.info("Starting email login authentication")
      data = request.get_json()

      # Required fields
      required_fields = ["username", "email", "mobile_number", "password"]
      for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({"error": f"{field} is required"}), 400

      username = data["username"].strip()
      email = data["email"].strip()
      mobile = data["mobile_number"].strip()
      password = data["password"].strip()

    #  # Email format validation
    #   if not is_valid_email(email):
    #    return jsonify({"error": "Invalid email format"}), 400
     # Additional field-specific validation
      email_validation = _validate_email_format(data["email"])
      if email_validation:
            return email_validation

     # Mobile number validation  
      if not re.match(r'^\d{10}$',data["mobile_number"]):
            return jsonify({"error": "Mobile must be 10 digits"}), 400

    # Password validation
      password_validation = _validate_password_strength(data["password"])
      if password_validation:
            return password_validation

    # Check username exists or not   
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

      return jsonify({"success": "true" , "message": "User registered successfully"}), 200
 
 except Exception as e:
        logger.error(f"Register failed for email with error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ----------------------------------------------------------------------------------------------------------

# ----------- Login

def handle_admin_login():
    try:
        logger.info("Starting email login authentication")

        #  Extract and validate request data
        data = request.get_json()
        if not data:
            logger.warning("Login attempt with empty request body")
            return jsonify({"error": get_error("invalid_data")}), 400

        email = data.get("email", "").strip()
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
        user.save()

        #  Return success
        logger.info(f"Admin login Successfully: {user.admin_uid}")
        return jsonify({
            "success": "true",
            "message": "Login successfully",
            "access_token": access_token,
            "session_id": session_id,
            "admin_uid": user.admin_uid,
            "username": user.username,
            "email": user.email,
        }), 200

    except Exception as e:
        logger.error(f"Login failed for email with error: {str(e)}")
        return jsonify({"error": get_error("login_failed")}), 500

