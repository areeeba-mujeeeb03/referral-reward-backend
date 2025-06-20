import uuid
import datetime
import smtplib
from email.mime.text import MIMEText
from twilio.base.values import unset
from main_app.models.user.user import User
from flask import request,jsonify


def forgot_password():
    data = request.json
    email = data.get("email")
    password_reset_token = str(uuid.uuid4())
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)

    User.update(token = password_reset_token, expiry = expiry)
    reset_link = f"http://127.0.0.1:4000/reset-password/{password_reset_token}"
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
    data = request.json
    email = data.get("email")
    new_password = data.get("new_password")

    user = User.objects(email = email).first()

    if not user:
        return jsonify({"message": "Invalid reset link"}), 404

    tokens = user.get("token")
    expiry = user.get("password_token_expires")
    if token !=  tokens:
        return jsonify({"error": "Unauthorized"}), 404
    if not expiry or datetime.datetime.now() > expiry:
        return jsonify({"message": "Reset link expired"}), 404

    user.update(set__password = new_password)
    user.update(unset__token =  True, unset__expiry = True)
    return jsonify({"message": "Password updated successfully!"}), 201