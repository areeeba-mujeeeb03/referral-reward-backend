import uuid
import datetime
import smtplib
from email.mime.text import MIMEText
from twilio.base.values import unset
from main_app.models.user.user import User
from main_app.models.user.links import Link
from flask import request,jsonify
from main_app.controllers.user.auth_controllers import _validate_password_strength
from main_app.utils.user.helpers import hash_password


def forgot_password():
    """
    Forgot password by user to send resent link on their email

    Process Flow:
    1. Validate request data and required fields
    2. Find user by email
    3. Check if email exists
    4. saves token in db
    5. Return verification result

    Expected JSON Request Body:
    {
        "email": "string (required)"
    }

    Returns:
        Flask Response: JSON response with verification status
        - Success (200): Password reset link sent to your email
        - Error (400): Failed to send email
        - Error (404): User not found
    """
    data = request.json
    email = data.get("email")
    password_reset_token = str(uuid.uuid4())
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)
    user = User.objects(email = data['email']).first()

    if not user:
        return jsonify({"success": False, "message": "User does not exist"})

    link = Link.objects(user_id = user.user_id).first()
    if not link:
        Link(
            user_id = user.user_id,
            token = password_reset_token,
            expiry = expiry,
            sent_at = datetime.datetime.now()
        ).save()
    else:
        link.update(
            set__token = password_reset_token,
            set__expiry = expiry
        ),

    reset_link = f"http://127.0.0.1:4000/login/reset-password/{password_reset_token}"
    email_body = (f"To change your password click on the link below/n"
                  f"{reset_link}")
    try:
        msg = MIMEText(email_body)
        msg["Subject"] = "Password Reset"
        msg["From"] = "saksheesharma1104@gmail.com"
        msg["To"] = "areebamujeeb309@gmail.com"
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("areebamujeeb309@gmail.com", "rvph suey zpfl smpw")
            server.sendmail("something3029@gmail.com", email, msg.as_string())
            return ({"message": "Password reset link sent to your email", "reset_token": reset_link}), 201
    except Exception as e:
        return ({"error": f"Failed to send email: {str(e)}"}), 404

def reset_password(token):
    """
    Forgot password by user to send resent link on their email

    Process Flow:
    1. Validate if the token in link matches the one stored in db
    2. Find user by email
    3. Check if token is same
    4. unset token, expiry in db and sets the date of last password updated on
    5. Return verification result

    Expected JSON Request Body:
    {
        "email": "string (required)",
        "new_password" : string(required)
    }

    Returns:
        Flask Response: JSON response with verification status
        - Success (200): Password updated successfully!
        - Error (404): Invalid reset link
        - Error (404) : Reset token not found
        - Error (400) : "Unauthorized
        - Error (404): User not found
    """
    data = request.json
    email = data.get("email")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    user = User.objects(email = email).first()
    if not user:
        return jsonify({"message": "User Not Found"}), 404

    password_validation = _validate_password_strength(new_password)
    if password_validation:
        return password_validation



    if new_password != confirm_password:
        return jsonify({"error": "Password do not match"}), 400

    print(token)
    link = Link.objects(user_id = user.user_id).first()
    if not link:
        return jsonify({"message": "Reset token not found"}), 404

    if token !=  link.token:
        return jsonify({"success" : False, "error": "Unauthorized"}), 404

    if datetime.datetime.now() > link.expiry:
        return jsonify({"message": "Reset link expired"}), 404
    hashed_password = hash_password(data["new_password"])

    user.update(set__password = hashed_password)
    link.update(unset__token =  True, unset__expiry = True, unset__sent_at = True,set__changed_on = datetime.datetime.now())
    return jsonify({"message": "Password updated successfully!"}), 201



