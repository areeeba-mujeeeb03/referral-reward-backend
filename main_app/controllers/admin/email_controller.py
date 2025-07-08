# from main_app.models.admin.
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os, logging
from main_app.models.admin.email_model import EmailTemplate

UPLOAD_FOLDER = "uploads/email_templates"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_email():
    try:
        logger.info("Create Email Template API called.")
        data = request.form

        email_type = data.get("email_type")
        name = data.get("name")
        email = data.get("email")
        subject = data.get("subject")
        reply_to = data.get("reply_to")
        content = data.get("content")
        button_text = data.get("button_text")
        button_url = data.get("button_url")
        image_type =data.get("image")

        if not email_type:
            logger.warning("email_type is missing in request.")
            return jsonify({"message": "email_type is required"}), 400
        
        if not all([name, email, subject, reply_to, content, button_text]):
            return jsonify({"message": "All feilds are required"}), 400
        
        image_path = None
        if "image" in request.files:
            image = request.files["image"]
            filename=secure_filename(image.filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image.save(filepath)
            image_path = filepath

        template =EmailTemplate.objects(email_type=email_type).first()
        if not template:
            template = EmailTemplate(email_type=email_type)
        print("template", template)

        template.name = name
        template.email = email
        template.reply_to = reply_to
        template.subject = subject
        template.content = content
        template.button_text = button_text
        template.button_url = button_url
        template.image_type = image_type
        if image_path:
            template.image_path = image_path

        template.save()
    
        logger.info(f"Email for type '{email_type}' saved successfully.")
        return jsonify({"message": "Email save successfully"}), 200
    
    except Exception as e:
        logger.error("Internal Server Error while saving email.")
        return jsonify({"error": "Internal server error"}), 500
