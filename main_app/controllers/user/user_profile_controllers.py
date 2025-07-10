import datetime
import os
from werkzeug.utils import secure_filename

from main_app.models.admin.error_model import Errors
from main_app.models.admin.help_model import FAQ, Contact
from flask import request, jsonify
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.product_model import Product
from main_app.utils.user.error_handling import get_error
import logging

from main_app.utils.user.helpers import check_password, hash_password

UPLOAD_FOLDER ="uploads/profile"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
UPLOAD_FOLDER = 'uploads/support_files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

import base64
import os
import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename

def update_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        if not user_id or not access_token or not session_id:
            return jsonify({"message": "Missing required fields", "success": False}), 400

        user = User.objects(user_id=user_id).first()

        if not user:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return jsonify({"success": False, "message": "Access token has expired"}), 401

        if user.access_token != access_token:
            return jsonify({"success": False, "message": "Invalid access token"}), 401

        if user.session_id != session_id:
            return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403

        password = data.get('password')
        if not password:
            return jsonify({"error": "Password is required to update profile"}), 400

        if not user.password.startswith("$2"):
            return jsonify({"success": False, "message": "Password hash is invalid. Please reset your password."}), 400

        if not check_password(password, user.password):
            Errors(
                username=user.username,
                email=user.email,
                error_source="Profile Update",
                error_type=f"Incorrect password attempt for: {user.email}"
            ).save()
            return jsonify({"error": get_error("incorrect_password")}), 400

        # Uniqueness checks
        if data.get("username") and User.objects(username=data["username"]).first():
            return jsonify({"error": get_error("username_exists")}), 400

        if data.get("email") and User.objects(email=data["email"]).first():
            return jsonify({"error": get_error("email_exists")}), 400

        if data.get("mobile_number") and User.objects(mobile_number=data["mobile_number"]).first():
            return jsonify({"error": "This number is already registered"}), 400

        update_fields = {}

        if data.get("username"):
            update_fields["username"] = data["username"]
        if data.get("email"):
            update_fields["email"] = data["email"]
        if data.get("mobile_number"):
            update_fields["mobile_number"] = data["mobile_number"]
        if data.get("new_password"):
            update_fields["password"] = hash_password(data["new_password"])

        if data.get("image"):
            try:
                image_data = data["image"]
                filename = f"{user_id}_profile.jpg"
                image_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))

                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(image_data))

                update_fields["profile_picture"] = f"/{image_path}"
            except Exception as e:
                return jsonify({"error": "Invalid image format or failed to save image", "details": str(e)}), 400

        if not update_fields:
            return jsonify({"success": False, "message": "No fields to update"}), 400

        user.update(**update_fields)

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "updated_fields": list(update_fields.keys())
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Server error", "error": str(e)}), 500


def redeem():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        product_id = data.get("product_id")

        user = User.objects(user_id = user_id).first()

        if not user:
            return jsonify({"success" : False, "message" : "User does not exist"})

        validate_session_token(user, access_token, session_id)

        reward = Product.objects()

        return jsonify({
            "success": True,
            "message": "Voucher Redeemed successfully!"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Server error", "error": str(e)}), 500


UPLOAD_FOLDER = "static/uploads/contact"

def submit_msg():
    data = request.get_json()

    # Required fields
    username = data.get('username')
    email = data.get('email')
    message = data.get('message')

    # Optional fields
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    files = [
        data.get("file1"),
        data.get("file2"),
        data.get("file3"),
        data.get("file4"),
        data.get("file5")
    ]
    files = [f for f in files if f]

    # Basic validation
    if not all([username, email, message]):
        return jsonify({"error": "All fields are required"}), 400

    user = User.objects(user_id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User does not exist"}), 404

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if user.access_token != access_token:
        return jsonify({"success": False, "message": "Invalid access token"}), 401

    if user.session_id != session_id:
        return jsonify({"success": False, "message": "Session mismatch"}), 403

    if user.username != username:
        return jsonify({"message": "You are not registered with this username"}), 400

    if user.email != email:
        return jsonify({"message": "You are not registered with this email"}), 400

    send = Contact(
        admin_uid=user.admin_uid,
        user_id=user_id,
        email=email,
        username=username,
        message=message,
        date=datetime.datetime.utcnow()
    ).save()

    file_urls = []
    if files:
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            for i, file_data in enumerate(files):
                base64_str = file_data.get("base64")
                original_filename = file_data.get("filename")

                if not base64_str or not original_filename:
                    continue

                safe_filename = secure_filename(f"{user_id}_{i+1}_{original_filename}")
                file_path = os.path.join(UPLOAD_FOLDER, safe_filename)

                with open(file_path, "wb") as f:
                    f.write(base64.b64decode(base64_str))

                file_urls.append(f"/{file_path}")
        except Exception as e:
            Errors(
                username=user.username,
                email=user.email,
                error_source="send contact message",
                error_type=f"Failed to save attachments {str(e)}"
            ).save()
            return jsonify({
                "error": "Failed to save attachments",
                "details": str(e)
            }), 400

        send.update(file_urls=file_urls)
        print(file_urls)
    return jsonify({"message": "Your query has been sent!"}), 201
