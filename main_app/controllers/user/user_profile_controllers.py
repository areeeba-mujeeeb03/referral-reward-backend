import datetime
from flask import request, jsonify
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token

from flask import request, jsonify
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token

def update_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        if not user_id or not access_token or not session_id:
            return jsonify({"success": False, "message": "Missing user_id, token, or session"}), 400

        # Validate access token and session
        is_valid, user, error_msg, status_code = validate_session_token(user_id, access_token, session_id)
        if not is_valid:
            return jsonify({"success": False, "message": error_msg}), status_code

        update_fields = {}

        if "username" in data:
            update_fields["set__username"] = data["username"].strip()
        if "email" in data:
            update_fields["set__email"] = data["email"].strip()
        if "mobile_number" in data:
            update_fields["set__mobile_number"] = data["mobile_number"].strip()
        if "profile_picture" in data:
            update_fields["set__profile_picture"] = data["profile_picture"].strip()

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
