# ----------- Exciting Prizes
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from main_app.models.admin.prize_model import ExcitingPrize
from main_app.models.admin.admin_model import Admin


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER ="uploads/prizes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def add_exciting_prizes():
    try:
        logger.info("Add Exciting Prizes API called")
        data = request.form
        title = data.get("title")
        term_conditions = data.get("term_conditions")
        admin_uid = data.get("admin_uid")
        required_meteors = data.get("required_meteors")
        # data_s = jsonify(data)
        print(data)

        if not all ([title , term_conditions, admin_uid, required_meteors]):
          return jsonify({"error": "All fields are required"}), 400

          # Validate meteors is numeric
        try:
            required_meteors = int(required_meteors)
        except ValueError:
            return jsonify({"error": "required_meteors must be a number"}), 400

         # Check user found or not
        if not Admin.objects(admin_uid=admin_uid).first():
            return jsonify({"error": "Admin not found" }), 400


        files = request.files.get("image")
        if not files:
            return jsonify({"error": "Image not found"}), 400
        prize = ExcitingPrize.objects(admin_uid=admin_uid).first()
        image_file = request.files.get("image")
        if image_file:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_path)
            image_url = f"/{image_path}"
        else:
            image_url = prize.image_url

        if prize:
            prize.update(
              title = title,
              image_url = image_url,
              term_conditions = term_conditions,
              required_meteors=required_meteors
            )
            msg = "Updated prize successfully"
        else:
             ExcitingPrize(
                 title=title,
                 term_conditions=term_conditions,
                 admin_uid=admin_uid,
                 image_url=image_url,
                 required_meteors=required_meteors
                ).save()
             msg = "Added prize successfully"


        logger.info(f"Prizes save with ID:")
        return jsonify({"success": "true" , "message": msg }), 200

    except Exception as e:
        print(e)
        logger.error(f"Add exciting prize failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500


    # -------------------------------------------------------------------------

def check_eligibility():
    data = request.get_json()
    user_meteors = data.get("meteors")
    admin_uid = data.get("admin_uid")

    prize = ExcitingPrize.objects(admin_uid=admin_uid).first()
    if not prize:
        return jsonify({"error": "Prize not found"}), 404

    if user_meteors >= prize.required_meteors:
        return jsonify({"eligible": True, "message": "User is eligible for this prize"}), 200
    else:
        return jsonify({"eligible": False, "message": "Not enough meteors"}), 200