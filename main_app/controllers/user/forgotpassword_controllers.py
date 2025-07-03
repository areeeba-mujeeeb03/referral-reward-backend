import uuid
import datetime
import smtplib
from email.mime.text import MIMEText
from twilio.base.values import unset

from main_app.controllers.user.OTP_controllers import _generate_otp
from main_app.models.user.user import User
from main_app.models.user.links import Link
from flask import request,jsonify
from main_app.controllers.user.auth_controllers import validate_password_strength
from main_app.utils.user.helpers import hash_password


def send_verification_code():
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
    verification_code = _generate_otp()
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)
    user = User.objects(email = data['email']).first()

    if not user:
        return jsonify({"success": False, "message": "User does not exist"})

    link = Link.objects(user_id = user.user_id).first()
    if not link:
        Link(
            user_id = user.user_id,
            verification_code = verification_code,
            expiry = expiry,
            sent_at = datetime.datetime.now()
        ).save()
    else:
        link.update(
            set__verification_code = verification_code,
            set__expiry = expiry
        ),

    email_body = (f"This is your verification code to change your password : "
                  f"{verification_code}")
    try:
        msg = MIMEText(email_body)
        msg["Subject"] = "Password Reset"
        msg["From"] = "saksheesharma1104@gmail.com"
        msg["To"] = "areebamujeeb309@gmail.com"
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("areebamujeeb309@gmail.com", "rvph suey zpfl smpw")
            server.sendmail("something3029@gmail.com", email, msg.as_string())
            return ({"message": f"Password verification code sent to {email}", "code": verification_code, "success" : True}), 201
    except Exception as e:
        return ({"error": f"Failed to send email: {str(e)}"}), 404


def verify_code():
    try:
        data = request.get_json()
        email = data.get("email")
        verification_code = data.get("verification_code")

        user = User.objects(email = email).first()
        if not user:
            return jsonify({"message" : "User not found"}), 400

        user_id = user.user_id
        print(user_id)

        link = Link.objects(user_id = user_id).first()
        code = link.verification_code

        if verification_code != link.verification_code:
            return jsonify({"message" : "Invalid code"})

        if not code:
            return jsonify({"message" : "resend verification code"})



        if datetime.datetime.now() > link.expiry:
            return jsonify({"message": "Reset code expired"}), 404

        link.update(unset__verification_code=True, unset__expiry=True, unset__sent_at=True, set__changed_on=datetime.datetime.now())
        return jsonify({"message" : "Verified Successfully", "success" : True}),200
    except Exception as e:
        return jsonify({"message" : f"An unexpected error occurred : {str(e)}"}), 400



def reset_password():
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

    password_validation = validate_password_strength(new_password)
    if password_validation:
        return password_validation

    if new_password != confirm_password:
        return jsonify({"error": "Password do not match"}), 400


    hashed_password = hash_password(data["new_password"])


    user.update(set__password = hashed_password)

    return jsonify({"message": "Password updated successfully!", "success" : True}), 201



