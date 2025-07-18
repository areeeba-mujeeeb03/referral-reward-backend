import os
from main_app.models.admin.error_model import Errors
from main_app.models.admin.help_model import FAQ, Contact
from main_app.models.admin.links import AppStats
from main_app.models.user.user import User
# from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.product_model import Product
from main_app.utils.user.error_handling import get_error
import logging
import datetime
from flask import request, jsonify
from main_app.utils.user.helpers import check_password, hash_password

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_profile():
    data = request.get_json()
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    if not user_id or not access_token or not session_id:
        return jsonify({"message": "Missing required fields", "success": False}), 400

    user = User.objects(user_id=user_id).first()
    try:
        if not user:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        if hasattr(user, 'expiry_time') and user.expiry_time:
            if datetime.datetime.now() > user.expiry_time:
                return jsonify({"success": False, "message": "Access token has expired",
                                "token": "expired"
                                }), 401

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
        if data.get("username")!= user.username and User.objects(username=data["username"]).first():
            return jsonify({"error": get_error("username_exists")}), 400

        if data.get("email")!= user.email and User.objects(email=data["email"]).first():
            return jsonify({"error": get_error("email_exists")}), 400

        if data.get("mobile_number")!= user.mobile_number and User.objects(mobile_number=data["mobile_number"]).first():
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
                update_fields["profile_picture"] = image_data
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
        Errors(username = user.username, email = user.email, error_type = str(e),  error_source="Update Profile",)
        return jsonify({"success": False, "message": "Server error"}), 500

def submit_msg():
    data = request.get_json()
    user_id = data.get("user_id")
    user = User.objects(user_id=user_id).first()
    try:


        username = data.get('username')
        email = data.get('email')
        message = data.get('message')

        access_token = data.get("mode")
        session_id = data.get("log_alt")

        files = [
            data.get("file1"),
            data.get("file2"),
            data.get("file3"),
            data.get("file4"),
            data.get("file5")
        ]
        print(data)
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
            date=datetime.datetime.now(),
            file_url = files
        )
        send.save()
        return jsonify({"message": "Your query has been sent!" , "success" : True}), 201

    except Exception as e:
        Errors(
            username=user.username,
            email=user.email,
            error_source="send contact message",
            error_type=f"Failed to save attachments {str(e)}"
        ).save()
        return jsonify({"message": "Failed to send query" , "success" : True}), 201

def update_app_stats(app_name, user):
    if app_name:
        app_col = AppStats.objects(admin_uid = user.admin_uid).first()
        for app in app_col.apps:
            print(app['platform'])
            if app['platform'].strip('').lower() == app_name.strip('').lower():
                print(app)
                app['accepted'] += 1
                app_col.save()
                return "done"

    return jsonify({"message" : "failed to update app status"}),400