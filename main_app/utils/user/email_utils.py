import uuid
import datetime
import smtplib
from email.mime.text import MIMEText
from main_app.models.user.user import User
from flask import request,jsonify


def forgot_password(email):
    password_reset_token = str(uuid.uuid4())
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=30)

    User.update_one({"$set": {"token": password_reset_token, "password_token_expires": expiry}},
        upsert=True
    )
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

def reset_password(token, user_id):
    data = request.json
    new_password = data.get("new_password")

    user = User.find_one({"user_id" : user_id})
    if not user:
        return jsonify({"message": "Invalid reset link"}), 404

    tokens = user.get("token")
    expiry = user.get("password_token_expires")
    if token !=  tokens:
        return jsonify({"error": "Unauthorized"}), 404
    if not expiry or datetime.datetime.now() > expiry:
        return jsonify({"message": "Reset link expired"}), 404
    User.update_one({"user_id": user_id}, {"$set": {"password": new_password}})
    User.update_one({"user_id": user_id},{"$unset" : {"token": token, "password_token_expires": expiry}})
    return jsonify({"message": "Password updated successfully!"}), 201


def send_error_email(subject, body, to_email):
    from_email = "your_email@example.com"
    password = "your_email_password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "areebamujeeb309@gmail.com"
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        print("Error email sent successfully.")
    except Exception as e:
        print("Failed to send email:", e)
