import uuid
import datetime
import smtplib
from email.mime.text import MIMEText
from twilio.base.values import unset
from main_app.models.user.user import User
from main_app.models.user.links import Link
from flask import request,jsonify


def forgot_password():
    data = request.json
    email = data.get("email")
    password_reset_token = str(uuid.uuid4())
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)
    user = User.objects(email = email).first()
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
    print(password_reset_token)
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

    print(token)
    link = Link.objects(user_id = user.user_id).first()
    if not link:
        return jsonify({"message": "Reset token not found"}), 404

    if token !=  link.token:
        return jsonify({"success" : False, "error": "Unauthorized"}), 404

    if datetime.datetime.now() > link.expiry:
        return jsonify({"message": "Reset link expired"}), 404

    user.update(set__password = new_password)
    link.update(unset__token =  True, unset__expiry = True, unset__sent_at = True,set__changed_on = datetime.datetime.now())
    return jsonify({"message": "Password updated successfully!"}), 201