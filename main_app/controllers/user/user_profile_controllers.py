import datetime
from itertools import product
from flask import request, jsonify

from main_app.models.user.reward import Reward
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.help_model import FAQ, Contact
from flask import request, jsonify
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.product_model import Product


def update_profile():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id= user_id).first()

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
        faqs = FAQ.objects()

        user = User.objects(user_id = user_id).first()
        if not user:
            return jsonify({"success" : False, "message" : "User does not exist"})

        validate_session_token(user, access_token, session_id)

        return jsonify([{"question": faq.question, "answer": faq.answer}for faq in faqs])

    except Exception as e:
        return jsonify({"success": False, "message": "Server error", "error": str(e)}), 500


def submit_msg():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    user_id = data.get("user_id")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    user = User.objects(user_id=user_id).first()
    if not user:
        return jsonify({"success": False, "message": "User does not exist"})

    validate_session_token(user, access_token, session_id)

    if not name or not email or not message:
        return jsonify({"error": "All fields are required"}), 400

    contact = Contact(name=name, email=email, message=message)
    contact.save()

    return jsonify({"message": "Your query has been received!"}), 201
