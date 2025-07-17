import logging 
from flask import request , jsonify 
from main_app.models.admin.admin_model import Admin
from main_app.utils.admin.helpers import generate_otp, get_expiry_time
from main_app.utils.user.error_handling import get_error
from main_app.utils.admin.mail import send_otp_email
import bcrypt
from datetime import datetime
from main_app.controllers.admin.admin_auth_controller import validate_password_strength

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------ Forgot Password

def forgot_otp_email():
    try:
        logger.info("Forgot OTP Email API called")
        data = request.get_json()
        email = data.get("email")
       
        # Email validation 
        if not email:
            logger.warning("Email field is empty")
            return jsonify({"message": "Email is required"}),400
        
        # Check email exist or not
        user = Admin.objects(email = email).first()
        if not user:
            logger.warning(f"User not found for email: {email}")
            return jsonify({"message": get_error("user_not_found")}), 400
        
        # Generate code
        code =  generate_otp()
        expiry_time = get_expiry_time()
        user.code = code
        user.code_expiry = expiry_time
        user.save()

        # send Email
        email_status = send_otp_email(email, code)
        if not email_status:
            logger.error(f"Failed to send OTP email to: {email}")
            return jsonify({"message": "Failed to send code"}), 500

        logger.info(f"OTP email sent successfully to: {email}")
        return jsonify({"message": "Code send successfully to email","success": "True"}), 200
    
    except Exception as e:
        logger.error(f"code send failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# ----------------------------------------------------------------------------------------------------

# ------- Verify code

def verify_otp():
  try:
    logger.info("Verify OTP API called")
    data = request.get_json()

    email = data.get("email", "").strip()
    code = data.get("code", "").strip()

    user = Admin.objects(email = email).first()
    if not user:
      logger.warning(f"No user found for email: {email}")
      return jsonify({"message": get_error("user_not_found")}), 400

    if user.code != code:
        return jsonify({"error": "Invalid code"}), 400

    if user.code_expiry < datetime.now():
        return jsonify({"message": "Code expired"}), 400

    logger.info(f"OTP verified successfully for user: {email}")
    return jsonify({"message": "Code verified", "success": "True"}), 200

  except Exception as e:
        logger.error(f"code verification failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# -----------------------------------------------------------------------------------------------------


# -----------Reset Password

def reset_password():
 try:
     logger.info("Reset password API called")
     data = request.get_json()

     email = data.get("email", "").strip()
     code = data.get("code")
     new_password = data.get("new_password", "")
     confirm_password = data.get("confirm_password", "")

     if not data:
         logger.warning("No data provided in request")
         return jsonify({"message": "No fields provided."}), 400

     user = Admin.objects(email = email).first()
     if not user:
        return jsonify({"error": "user_not_found"}), 400

     password_validation = validate_password_strength(data["new_password"])
     if password_validation:
            return password_validation

     if new_password != confirm_password:
      logger.warning("Passwords do not match")
      return jsonify({"message": "Password do not match"}), 400
    
    
     salt = bcrypt.gensalt(rounds=12)
     hashed = bcrypt.hashpw(new_password.encode(), salt)

     if user.code != code:
         return jsonify({"error": "Invalid code for this email"}), 400


     user.password = hashed.decode()
     user.code = None
     user.code_expiry = None
     user.save()

     logger.info(f"Password reset successful for email: {email}")
     return jsonify({"success": "true" ,"message": "Password reset successfully",}), 200
  
 except Exception as e:
         logger.error(f"Password reset failed:{str(e)}")
         return jsonify({"error": "Internal server error"}), 500