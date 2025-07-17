import datetime
from flask import request, jsonify
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.error_model import Errors
from main_app.utils.user.error_handling import get_error
from main_app.utils.user.helpers import check_password, hash_password

def edit_profile_data():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        password = data.get('password')

        admin = Admin.objects(admin_uid=admin_uid).first()

        if not admin_uid or not access_token or not session_id:
            return jsonify({"message": "Missing required fields", "success": False}), 400

        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        if hasattr(admin, 'expiry_time') and admin.expiry_time:
            if datetime.datetime.now() > admin.expiry_time:
                return jsonify({"success": False, "message": "Access token has expired"}), 401

        if admin.access_token != access_token:
            return jsonify({"success": False, "message": "Invalid access token"}), 401

        if admin.session_id != session_id:
            return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403


        if not password:
            return jsonify({"error": "Password is required to update profile"}), 400

        if not admin.password.startswith("$2"):
            return jsonify({"success": False, "message": "Password hash is invalid. Please reset your password."}), 400

        if not check_password(password, admin.password):
            Errors(
                username=admin.username,
                email=admin.email,
                error_source="Profile Update",
                error_type=f"Incorrect password attempt for: {admin.email}"
            ).save()
            return jsonify({"error": get_error("incorrect_password")}), 400

        # Uniqueness checks
        if data.get("username") != admin.username and Admin.objects(username=data["username"]).first():
            return jsonify({"error": get_error("username_exists")}), 400

        if data.get("email") != admin.email and Admin.objects(email=data["email"]).first():
            return jsonify({"error": get_error("email_exists")}), 400

        if data.get("mobile_number")!= admin.mobile_number and Admin.objects(mobile_number=data["mobile_number"]).first():
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

        image = data.get("image")

        if "image" in data:
            update_fields["profile_picture"] = image

        if not update_fields:
            return jsonify({"success": False, "message": "No fields to update"}), 400

        admin.update(**update_fields)

        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "updated_fields": list(update_fields.keys())
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": "Server error", "error": str(e)}), 500

