import logging 
from flask import request , jsonify 
from main_app.models.admin.admin_model import Admin
from main_app.utils.admin.helpers import generate_otp, get_expiry_time
from main_app.utils.user.error_handling import get_error
from main_app.utils.admin.mail import send_otp_email
import bcrypt
from datetime import datetime
from main_app.controllers.admin.admin_auth_controller import _validate_password_strength

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ------ Forgot Password

def forgot_otp_email():
    try:
        data = request.get_json()
        email = data.get("email", "").strip()
       
        # Email validation 
        if not email:
            return jsonify({"error": "Email is required"}),400
        
        # Check email exist or not
        user = Admin.objects(email = email).first()
        if not user:
            return jsonify({"error": get_error("user_not_found")}), 400
        
        # Generate code
        code =   generate_otp()
        expiry_time = get_expiry_time()
        user.code = code
        user.code_expiry = expiry_time
        user.save()

        # send Email
        email_status = send_otp_email(email, code)
        if not email_status:
            return jsonify({"error": "Failed to send code"}), 500
        
        return jsonify({
            "message": "Code send successfully to email",
            "success": "True"
        }), 200
    
    except Exception as e:
        logger.error(f"code send failed:{str(e)}")
        return jsonify({"errro": "Internal server error"}), 500

# ----------------------------------------------------------------------------------------------------

# ------- Verify code

def verify_otp():
  try:
    data = request.get_json()
    email = data.get("email", "").strip()
    code = data.get("code", "").strip()

    user = Admin.objects(email = email).first()
    if not user:
      return jsonify({"error": get_error("user_not_found")}), 400

    if not user or user.code != code:
     return jsonify({"error": "Invalid code"}), 400
    
    if user.code_expiry < datetime.now():
        return jsonify({"error": "Code expired"}), 400
    
    return jsonify({"error": "Code verified", "success": "True"}), 200

  except Exception as e:
        logger.error(f"code varification failed:{str(e)}")
        return jsonify({"errro": "Internal server error"}), 500


# -----------------------------------------------------------------------------------------------------


# -----------Reset Password

def reset_password():
 try:
     data = request.get_json()
     email = data.get("email", "").strip()
     new_password = data.get("new_password", "")
     confirm_password = data.get("confirm_password", "")

     if not data:
         return jsonify({"error": "No fields provided."}), 400

     user = Admin.objects(email = email).first()
     if not user:
        return jsonify({"error": "user_not_found"}), 400
    
     password_validation = _validate_password_strength(data["new_password"])
     if password_validation:
            return password_validation

     if new_password != confirm_password:
      return jsonify({"error": "Password do not match"}), 400
    
    
     salt = bcrypt.gensalt(rounds=12)
     hashed = bcrypt.hashpw(new_password.encode(), salt)

     user.password = hashed.decode()
     user.code = None
     user.code_expiry = None
     user.save()

     return jsonify({"success": "true" ,"message": "Password reset successfully",}), 200
  
 except Exception as e:
         logger.error(f"Password reset failed:{str(e)}")
         return jsonify({"errro": "Internal server error"}), 500





def edit_email_body():
    return