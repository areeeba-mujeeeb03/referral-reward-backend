
import smtplib
from email.mime.text import MIMEText

def send_otp_email(recipient, code):
    sender_email = "nabirkhan1662@gmail.com"
    sender_password = "iulh zxvz hpxi ejlk"
    subject = "Your code for Password Reset"
    body = f"Your code is: {code}\nIt is valid for 5 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False