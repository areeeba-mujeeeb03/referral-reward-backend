import bcrypt
from flask import request, jsonify
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.campaign_model import Campaign
from main_app.utils.user.helpers import hash_password, check_password,generate_access_token,create_user_session
from main_app.utils.user.error_handling import get_error
import logging
import datetime
import re
from main_app.controllers.user.auth_controllers import validate_password_strength, validate_email_format
from main_app.utils.user.string_encoding import generate_encoded_string

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SESSION_EXPIRY_MINUTES = 30
#------- Register 

def admin_register():
 try:
      logger.info("Starting email login authentication")
      data = request.get_json()

      # Required fields
      required_fields = ["username", "email", "mobile_number", "password"]
      for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({"message": f"{field} is required"}), 400


     # Additional field-specific validation
      email_validation = validate_email_format(data["email"])
      if email_validation:
            return email_validation

     # Mobile number validation  
      if not re.match(r'^\d{10}$',data["mobile_number"]):
            return jsonify({"message": "Mobile must be 10 digits"}), 400

    # Password validation
      password_validation = validate_password_strength(data["password"])
      if password_validation:
            return password_validation

    # Check username exists or not   
      if Admin.objects(username=data["username"]).first():
        return jsonify({"message": get_error("username_exists")}), 400
    
      if Admin.objects(email=data["email"]).first():
        return jsonify({"message": get_error("email_exists")}), 400

      if Admin.objects(mobile_number=data["mobile_number"]).first():
        return jsonify({"message": "mobile number already exists", "success" : False}), 400

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


# ------------------------------------------------------------------------------------------- #

# ----------- Login ----------- #

def handle_admin_login():
    try:
        logger.info("Starting email login authentication")
        data = request.get_json()
        if not data:
            logger.warning("Login attempt with empty request body")
            return jsonify({"message": get_error("invalid_data")}), 400

        email = data.get("email")
        password = data.get("password")

        #  Validate required fields
        if not email or not password:
            return jsonify({
                "message": "Email and password are required",
                "missing_fields": ["email", "password"]
            }), 400

        #  Find user by email
        user = Admin.objects(email=email).first()
        if not user:
            logger.warning(f"Login attempt with unknown email: {email}")
            return jsonify({"message": get_error("user_not_found")}), 404

        #  Check password
        if not check_password(password, user.password):
            logger.warning(f"Incorrect password attempt for: {email}")
            return jsonify({"message": get_error("incorrect_password")}), 400

        #  Return success
        logger.info(f"Admin login Successfully: {user.admin_uid}")
        return jsonify({
            "success": "true",
            "admin_uid" : user.admin_uid,
            "message": "Login successfully"
        }), 200

    except Exception as e:
        logger.error(f"Login failed for email with error: {str(e)}")
        return jsonify({"error": get_error("login_failed")}), 500

def handle_authentication():
    data = request.get_json()
    admin_uid = data.get("admin_uid")

    existing = Admin.objects(admin_uid=admin_uid).first()

    if not existing:
        logger.warning("User not found")
        return jsonify({"message": get_error("user_not_found")}), 404


    #  Generate tokens
    access_token = generate_access_token(existing.admin_uid)
    session_id = create_user_session(existing.admin_uid)
    expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)
    #  Update user session info in DB
    existing.access_token = access_token
    existing.session_id = session_id
    existing.expiry_time = expiry_time
    existing.last_login = datetime.datetime.now()
    existing.save()

    return jsonify({"log_alt" : session_id,
                    "mode" : access_token,
                    "success": True}), 200


# def handle_authentication():
#     data = request.get_json()
#     admin_uid = data.get("admin_uid")
#
#     existing = Admin.objects(admin_uid = admin_uid).first()
#
#     if not existing:
#         logger.warning("User not found")
#         return jsonify({"message": get_error("user_not_found")}), 404
#
#     #  Generate tokens
#     access_token = generate_access_token(existing.admin_uid)
#     session_id = create_user_session(existing.admin_uid)
#     expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)
#     #  Update user session info in DB
#     existing.access_token = access_token
#     existing.session_id = session_id
#     existing.expiry_time = expiry_time
#     existing.last_login = datetime.datetime.now()
#     existing.save()
#
#     part1 = access_token[:10]
#     part2 = access_token [10:]
#
#     info = {"access_token": bcrypt.hashpw((part2+part1).encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
#             "session_id": session_id,
#             "admin_uid" : admin_uid}
#
#     fields_to_encode = ["access_token", "session_id"]
#     print(info)
#
#     res = generate_encoded_string(info, fields_to_encode)
#     return jsonify({"logs": res,
#                     "success" : True}),200

# def check_authentication(admin_uid, access_token, session_id):
#     data = request.get_json()
#
#     existing = Admin.objects(admin_uid = admin_uid).first()
#
#     if not existing:
#         logger.warning("User not found")
#         return jsonify({"message": get_error("user_not_found")}), 404
#
#     ## Generate tokens
#     access_token = generate_access_token(existing.admin_uid)
#     session_id = create_user_session(existing.admin_uid)
#     expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=SESSION_EXPIRY_MINUTES)
#     ## Update user session info in DB
#     existing.access_token = access_token
#     existing.session_id = session_id
#     existing.expiry_time = expiry_time
#     existing.last_login = datetime.datetime.now()
#     existing.save()
#
#     part1 = access_token[:len(access_token)/2]
#     part2 = access_token [len(access_token)/2:]
#     print(part1)
#     print(part2)
#
#     info = {"access_token": bcrypt.hashpw((part1+part2).encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
#             "session_id": session_id,
#             "admin_uid" : admin_uid}
#
#     fields_to_encode = ["access_token", "session_id"]
#     print(info)
#
#     res = generate_encoded_string(info, fields_to_encode)
#     return jsonify({"logs": res,
#                     "success" : True}),200
