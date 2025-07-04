import os
import re
from flask import request, jsonify
from werkzeug.utils import secure_filename
from main_app.controllers.user.auth_controllers import validate_session_token, validate_password_strength, validate_email_format
from main_app.models.admin.admin_model import Admin
from main_app.utils.user.error_handling import get_error

UPLOAD_FOLDER ="uploads/profile"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def edit_profile_data():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        # access_token = data.get("mode")
        # session_id = data.get("log_alt")

        admin = Admin.objects(admin_uid=admin_uid).first()

        if not admin:
            return jsonify({"success": False, "message": "User does not exist"})

        if not update_fields:
            return jsonify({"success": False, "message": "No fields to update"}), 400

        email_validation = validate_email_format(data["email"])
        if email_validation:
            return email_validation

        # Mobile number validation
        if not re.match(r'^\d{10}$', data["mobile_number"]):
            return jsonify({"error": "Mobile must be 10 digits"}), 400

        # Password validation
        password_validation = validate_password_strength(data["password"])
        if password_validation:
            return password_validation

        # Check username exists or not
        if Admin.objects(username=data["username"]).first():
            return jsonify({"error": get_error("username_exists")}), 400

        if Admin.objects(email=data["email"]).first():
            return jsonify({"error": get_error("email_exists")}), 400

        if Admin.objects(mobile_number=data["mobile_number"]).first():
            return jsonify({"error": get_error("mobile_number_exists")}), 400

        update_fields = {}

        if "username" in data:
            update_fields["username"] = data["username"]
        if "email" in data:
            update_fields["email"] = data["email"]
        if "mobile_number" in data:
            update_fields["mobile_number"] = data["mobile_number"]


        files = request.files.get("image")
        if not files:
            return jsonify({"error": "Image not found"}), 400

        filename = secure_filename(files.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        files.save(image_path)
        img_file = f"/{image_path}"

        if "image" in data:
            update_fields["profile_picture"] = img_file

        admin.update(**update_fields)

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "updated_fields": list(update_fields.keys())
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Server error", "error": str(e)}), 500

