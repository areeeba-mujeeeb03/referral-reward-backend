from flask import request, jsonify
from main_app.models.admin.admin_model import Admin
from main_app.utils.user.helpers import hash_password, check_password,generate_access_token,create_user_session
from main_app.utils.user.error_handling import get_error
import logging
import datetime
import re

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{3,}$'
    return re.match(pattern, email) is not None

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
      email = data["email"].strip().lower()
      mobile = data["mobile_number"].strip()
      password = data["password"].strip()

     # Email format validation
      if not is_valid_email(email):
       return jsonify({"error": "Invalid email format"}), 400
      
     # Mobile number validation  
      if not re.match(r'^\d{10}$',data["mobile_number"]):
            return jsonify({"error": "Mobile must be 10 digits"}), 400

    # 
    #   password_validation = _validate_password_strength(data["password"])
    #   if password_validation:
    #         return password_validation

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

      return jsonify({"message": "User registered successfully"}), 200
 
 except Exception as e:
        logger.error(f"Login failed for email with error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



# ==================

# Password Strength Validation Utility

# # ==================
# def _validate_password_strength(password):
#     """
#     Validate password meets minimum security requirements
    
#     Password Requirements:
#     - Minimum 8 characters length
#     - At least one uppercase letter
#     - At least one lowercase letter  
#     - At least one numeric digit
    
#     Args:
#         password (str): Password to validate
        
#     Returns:
#         Flask Response or None: Error response if weak, None if strong
#     """
#     if len(password) < 8:
#         return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
#     if not any(c.isupper() for c in password):
#         return jsonify({"error": "Password must contain at least one uppercase letter"}), 400
    
#     if not any(c.islower() for c in password):
#         return jsonify({"error": "Password must contain at least one lowercase letter"}), 400
    
#     if not any(c.isdigit() for c in password):
#         return jsonify({"error": "Password must contain at least one number"}), 400
    
#     return None



# //----------------------------------------------------------------------------------------------------------




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

