# from main_app.models.admin.
import datetime

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os, logging

from main_app.models.admin.admin_model import Admin
from main_app.models.admin.email_model import EmailTemplate

UPLOAD_FOLDER = "uploads/email_templates"

logging.basicConfig(level=logging.INFO)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logger = logging.getLogger(__name__)

def create_email():
    try:
        logger.info("Create Email Template API called.")
        data = request.form
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        email_type = data.get("email_type")
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        reply_to = data.get("reply_to")
        content = data.get("content")
        button_text = data.get("button_text")
        button_url = data.get("button_url")
        image_type =data.get("image_type")
        image = data.get("image")

        exist = Admin.objects(admin_uid=admin_uid).first()

        if not exist:
            return jsonify({"success": False, "message": "User does not exist"})

        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400

        if exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(exist, 'expiry_time') and exist.expiry_time:
            if datetime.datetime.now() > exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired",
                         "token": "expired"}), 401

        if not email_type:
            logger.warning("email_type is missing in request.")
            return jsonify({"message": "email_type is required"}), 400
        
        if not all([name, email, subject, reply_to, content, button_text]):
            return jsonify({"message": "All feilds are required"}), 400

        template =EmailTemplate.objects(email_type=email_type).first()
        if not template:
            template = EmailTemplate(email_type=email_type)
        print("template", template)

        template.name = name
        template.email = email
        template.subject = subject
        template.reply_to = reply_to
        template.content = content
        template.button_text = button_text
        template.button_url = button_url
        template.image_type = image_type
        if image:
            template.image_path = image

        template.save()
    
        logger.info(f"Email for type '{email_type}' saved successfully.")
        return jsonify({"message": "Email save successfully"}), 200
    
    except Exception as e:
        logger.error(f"Internal Server Error while saving email.{str(e)}")
        return jsonify({"error": "Internal server error"}), 500
