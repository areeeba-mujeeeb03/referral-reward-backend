from flask import request , jsonify
import os
import logging
from werkzeug.utils import secure_filename
from main_app.models.admin.how_it_work_model import HowItWork 
from main_app.models.admin.advertisment_card_model import AdvertisementCard
from main_app.models.admin.admin_model import Admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_how_it_work():
    try:
        logger.info(f"Add and update how it work API called for uid:")
        data = request.get_json()
        title1 = data.get("title1")
        desc1 = data.get("desc1")
        title2 = data.get("title2")
        desc2 = data.get("desc2")
        title3 = data.get("title3")
        desc3 = data.get("desc3")
        admin_uid = data.get("admin_uid")
        
        if not data:
            return jsonify({"error": "No fields provided"}), 400

        # Validaiton
        if not all([admin_uid, title1, desc1, title2, desc2, title3, desc3 ]):
         return jsonify({"error": " All fields are required."}), 400
        
        # Check user found or not 
        if not Admin.objects(admin_uid=admin_uid).first():
            return jsonify({"error": "Admin not found" }), 400
         
        # Check if document exists
        existing = HowItWork.objects(admin_uid=admin_uid).first()
        if existing:
            existing.update(
                title1=data['title1'],
                desc1=data['desc1'],
                title2=data['title2'],
                desc2=data['desc2'],
                title3=data['title3'],
                desc3=data['desc3']
            )
            msg = "Updated successfully"
        else:
            HowItWork(**data).save()
            msg = "Added successfully"

        logger.info(f"How it work saved with ID")
        return jsonify({"success": "true" ,"message": msg}), 200

    except Exception as e:
        logger.error(f"how it work failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ------------------------------------------------------------------------------------------------------

# Advertisement card

UPLOAD_FOLDER = "uploads/advertisement_card"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def advertisement_card():
    try:
      logger = logging.getLogger(__name__)
      
      data = request.form
      title = data.get("title")
      description = data.get("description")
      button_txt = data.get("button_txt")
      admin_uid = data.get("admin_uid")
      
      if not all([title, description, button_txt, admin_uid]):
         return jsonify({"error": "All fields are required."}), 400
      
        # Check user found or not 
      if not Admin.objects(admin_uid=admin_uid).first():
            return jsonify({"error": "Admin not found" }), 400
      
       # Image upload
      image = request.files.get("image_url")
      image_url = ""
      if not image:
        return jsonify({"error": "No image uploaded"}), 400
         
      filename = secure_filename(image.filename)
      image_path = os.path.join(UPLOAD_FOLDER, filename)
      image.save(image_path)
      image_url = f"/{image_path}"    
      
       # Check if document exists
      existing = AdvertisementCard.objects(admin_uid=admin_uid).first()
      if existing:
            existing.update(
                title=title,
                description=description,
                button_txt=button_txt,
                image_url=image_url
            )
            msg = "Updated advertisment card successfully"
      else:
            AdvertisementCard( 
                title=title,
                description=description,
                button_txt=button_txt,
                admin_uid=admin_uid,
                image_url=image_url  
            ).save()
            msg = "Added advertisment card successfully"
      

      return jsonify({"message": msg, "success": "true"}), 200
    
    except Exception as e:
       logger.error(f"Add advertisment card failed : {str(e)}")
       return jsonify({"error": "Internal server error"}), 500