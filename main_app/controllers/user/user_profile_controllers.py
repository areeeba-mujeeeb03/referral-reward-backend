import datetime
import os
from itertools import product
from flask import request, jsonify
from werkzeug.utils import secure_filename
from main_app.models.user.reward import Reward
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.help_model import FAQ, Contact
from flask import request, jsonify
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.product_model import Product
from main_app.utils.user.error_handling import get_error

UPLOAD_FOLDER ="uploads/profile"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def update_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id= user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})

        # Check username exists or not
        if User.objects(username=data["username"]).first():
            return jsonify({"error": get_error("username_exists")}), 400

        if User.objects(email=data["email"]).first():
            return jsonify({"error": get_error("email_exists")}), 400

        if User.objects(mobile_number=data["mobile_number"]).first():
            return jsonify({"error": get_error("mobile_number_exists")}), 400

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401
        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

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

        if not update_fields:
            return jsonify({"success": False, "message": "No fields to update"}), 400

        user_exist.update(**update_fields)

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


def help_faq():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        faqs = FAQ.objects()

        return jsonify([{"a": faq.question, "b": faq.answer}for faq in faqs])

    except Exception as e:
        return jsonify({"success": False, "message": "Server error", "error": str(e)}), 500


def submit_msg():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    message = data.get('message')
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user_exist = User.objects(user_id=user_id).first()


    if not username or not email or not message:
        return jsonify({"error": "All fields are required"}), 400

    if not user_exist:
        return jsonify({"success": False, "message": "User does not exist"})
    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400
    if user_exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if user_exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if user_exist.username != username :
        return jsonify({"message" : "You are not registered with this username"})

    if user_exist.email != email:
        return jsonify({"message" : "You are not registered with this email"})


    contact = Contact(user_id = user_id, username=username, email=email, message=message)

    contact.save()

    return jsonify({"message": "Your query has been sent!"}), 201
