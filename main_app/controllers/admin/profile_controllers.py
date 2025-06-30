from flask import request, jsonify
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.admin_model import Admin


def edit_profile_data():
    try:
        data = request.get_json()
        admin_id = data.get("admin_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        admin = Admin.objects(admin_id=admin_id).first()

        if not admin:
            return jsonify({"success": False, "message": "User does not exist"})
        validate_session_token(admin, access_token, session_id)

        update_fields = {}

        if "username" in data:
            update_fields["username"] = data["username"]
        if "email" in data:
            update_fields["email"] = data["email"]
        if "mobile_number" in data:
            update_fields["mobile_number"] = data["mobile_number"]
        if "profile_picture" in data:
            update_fields["profile_picture"] = data["profile_picture"]

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
