# ----------- Exciting Prizes

from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from main_app.models.admin.prize_model import ExcitingPrize


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
        terms_conditions = data.get("terms_conditions")

        if not title:
          return jsonify({"error": "Title not found"}), 400
        
        files = request.files.get("image")
        if not files:
            return jsonify({"error": "Image not found"}), 400
        
        filename = secure_filename(files.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        files.save(image_path)
        image_url = f"/{image_path}"

        prize = ExcitingPrize(
            title = title,
            image_url = image_url,
            terms_conditions = terms_conditions
        )
        prize.save()
        print("prize", prize)
        logger.info(f"Prizes save with ID: {str(prize.id)}")
        return jsonify({"message": "Prize add successfully", }), 200

    except Exception as e:
        logger.error(f"Add exciting prize failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500   