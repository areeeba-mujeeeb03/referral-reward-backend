import logging 
from flask import request , jsonify 
from main_app.models.admin.admin_model import Admin
from main_app.utils.admin.helpers import generate_otp, get_expiry_time
from main_app.utils.user.error_handling import get_error
from main_app.utils.admin.mail import send_otp_email
import bcrypt
from datetime import datetime

logger = logging.getLogger(__name__)

# ------ Forgot Password

def forgot_otp_email():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
       
        # email validation 
        if not email:
            return jsonify({"error": "Email is required"}),400
        
        # Check email exist or not
        user = Admin.objects(email = email).first()
        if not user:
            return jsonify({"error": get_error("user_not_found")}), 400
        
        # GEnerate OTP
        otp =   generate_otp()
        expiry_time = get_expiry_time()
        user.otp = otp
        user.otp_expiry = expiry_time
        user.save()

        # send Email
        email_status = send_otp_email(email, otp)
        if not email_status:
            return jsonify({"error": "Failed to send OTP"}), 500
        
        return jsonify({
            "message": " OTP send successfully to email",
            "success": "True",
            "otp": otp,
            "expiry_time": expiry_time.isoformat()
        }), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()  
        logger.error(f"OTP send failed:{str(e)}")
        return jsonify({"errro": "Internal server error"}), 500

# ----------------------------------------------------------------------------------------------------

# ------- Verify OTP

def verify_otp():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    user = Admin.objects(email = email).first()
    if not user or user.otp != otp:
     return jsonify({"error": "Invalid OTP"}), 400
    
    if user.otp_expiry < datetime.now():
        return jsonify({"error": "Code expired"}), 400
    
    return jsonify({"error": "Code verified", "success": "True"}), 200

# -----------------------------------------------------------------------------------------------------

# -----------Reset Password

def reset_password():
 try:
     data = request.get_json()
     email = data.get("email", "").strip().lower()
     new_password = data.get("new_password", "")
     confirm_password = data.get("confirm_password", "")

     if new_password != confirm_password:
      return jsonify({"error": "Password do not match"}), 400
    
     user = Admin.objects(email = email).first()
     if not user:
        return jsonify({"error": "user_not_found"}), 400
    
    
     salt = bcrypt.gensalt(rounds=12)
     hashed = bcrypt.hashpw(new_password.encode(), salt)

     user.password = hashed.decode()
     user.otp = None
     user.otp_expiry = None
     user.save()

     return jsonify({"errro": "Password reset successfully", "success": "True"}), 200
  
 except Exception as e:
         logger.error(f"Password reset failed:{str(e)}")
         return jsonify({"errro": "Internal server error"}), 500




def edit_email_body():
    return