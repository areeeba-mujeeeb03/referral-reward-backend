# ----------- Exciting Prizes

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from main_app.models.admin.prize_model import PrizeDetail, AdminPrizes
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

        #  Validation fields
        if not all ([title , term_conditions, admin_uid, required_meteors]):
          logger.warning("Missing required fields.")
          return jsonify({"error": "All fields are required"}), 400
        
          # Validate meteors is numeric
        try:
            required_meteors = int(required_meteors)
        except ValueError:
            logger.warning("Invalid required_meteors: must be an integer.")
            return jsonify({"error": "required_meteors must be a number"}), 400

         # Check user found or not 
        if not Admin.objects(admin_uid=admin_uid).first():
            logger.warning(f"Admin not found for UID: {admin_uid}")
            return jsonify({"error": "Admin not found" }), 400
      

        files = request.files.get("image")
        image_url = None
        # if not files:
        #     return jsonify({"error": "Image not found"}), 400
        if files:
            filename = secure_filename(files.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            files.save(image_path)
            image_url = f"/{image_path}"

          # Fetch existing admin prizes
        admin_prize = AdminPrizes.objects(admin_uid=admin_uid).first()
        updated = False

        if admin_prize:
            # Check if a prize with same title exists → update it
            for prize in admin_prize.prizes:
                if prize.title == title:
                    prize.term_conditions = term_conditions
                    prize.required_meteors = required_meteors
                    if image_url:
                        prize.image_url = image_url
                    updated = True
                    break

            if updated:
                admin_prize.save()
                msg = "Prize updated successfully"
            else:
                # Add new prize
                new_prize = PrizeDetail(
                    title=title,
                    term_conditions=term_conditions,
                    image_url=image_url,
                    required_meteors=required_meteors
                )
                admin_prize.prizes.append(new_prize)
                admin_prize.save()
                msg = "New prize added to existing admin"
        else:
            # First time prize creation for admin
            new_prize = PrizeDetail(
                title=title,
                term_conditions=term_conditions,
                image_url=image_url,
                required_meteors=required_meteors
            )
            AdminPrizes(admin_uid=admin_uid, prizes=[new_prize]).save()
            msg = "Prize list created for new admin"

        logger.info(f"Prize added for admin_uid: {admin_uid}")
        return jsonify({"success": True, "message": msg}), 200

    except Exception as e:
        logger.error(f"Add exciting prize failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500   
    

    # -------------------------------------------------------------------------

def check_eligibility():
    try:
        logger.warning(f"Check meteors for user:")
        data = request.get_json()

        user_meteors = data.get("meteors")
        admin_uid = data.get("admin_uid")

        prize = AdminPrizes.objects(admin_uid=admin_uid).first()
        if not prize:
            logger.warning(f"Prize not found")
            return jsonify({"message": "Prize not found"}), 404

        if user_meteors >= prize.required_meteors:
            return jsonify({"eligible": True, "message": "User is eligible for this prize"}), 200
        else:
            return jsonify({"eligible": False, "message": "Not enough meteors"}), 200

    except Exception as e:
        logger.error(f"Check meteors failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500