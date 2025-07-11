from flask import request, jsonify
from werkzeug.utils import secure_filename
from main_app.models.admin.perks_model import ExclusivePerks
import os , logging
from main_app.models.admin.admin_model import Admin


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads/exclusive_perks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def create_discount_coupons():
    data = request.form
    title = data.get("title")
    information = data.get("information")
    term_conditions = data.get("term_conditions")
    admin_uid = data.get("admin_uid")

    if not all ([title , term_conditions, information, admin_uid]):
            logger.warning("Missing required fields.")
            return jsonify({"message": "All fields are required"}), 400

    if not Admin.objects(admin_uid=admin_uid).first():
        logger.warning(f"Admin not found for UID: {admin_uid}")
        return jsonify({"message": "Admin not found" }), 400

    upload = request.files.get("image")
    image_url = None
    if upload:
        filename = secure_filename(upload.filename)
        image_path  = os.path.join(UPLOAD_FOLDER, filename)
        upload.save(image_path)
        image_url = f"/{image_path}"

      # Check if a similar perk exists for the admin
    existing_perk = ExclusivePerks.objects(title=title, admin_uid=admin_uid).first()
    if existing_perk:
         existing_perk.update(
               information=information,
               term_conditions=term_conditions,
               image=image_url
          )
         message = "Exclusive perks updated successfully"
    else:
        new_perk = ExclusivePerks(
               title=title,
               information=information,
               term_conditions=term_conditions,
               image=image_url,
               admin_uid=admin_uid
         )
        new_perk.save()
        message = "Exclusive perk added successfully"

    return jsonify({"success": True, "message": message}), 200

def create_exclusive_perks():
     try:
        data = request.form
        title = data.get("title")
        information = data.get("information")
        term_conditions = data.get("term_conditions")
        admin_uid = data.get("admin_uid")

        #  Validation fields
        if not all ([title , term_conditions, information, admin_uid]):
                logger.warning("Missing required fields.")
                return jsonify({"message": "All fields are required"}), 400
                
        # Check user found or not 
        if not Admin.objects(admin_uid=admin_uid).first():
            logger.warning(f"Admin not found for UID: {admin_uid}")
            return jsonify({"message": "Admin not found" }), 400

        upload = request.files.get("image")
        image_url = None
        if upload:
            filename = secure_filename(upload.filename)
            image_path  = os.path.join(UPLOAD_FOLDER, filename)
            upload.save(image_path)
            image_url = f"/{image_path}"

          # Check if a similar perk exists for the admin
        existing_perk = ExclusivePerks.objects(title=title, admin_uid=admin_uid).first()
        if existing_perk:
             existing_perk.update(
                   information=information,
                   term_conditions=term_conditions,
                   image=image_url
              )
             message = "Exclusive perks updated successfully"
        else:
            new_perk = ExclusivePerks(
                   title=title,
                   information=information,
                   term_conditions=term_conditions,
                   image=image_url,
                   admin_uid=admin_uid
             )
            new_perk.save()
            message = "Exclusive perk added successfully"

        return jsonify({"success": True, "message": message}), 200
    

     except Exception as e:
            logger.error(f"Add exclusive perks failed:{str(e)}")
            return jsonify({"error": "Internal server error"}), 500