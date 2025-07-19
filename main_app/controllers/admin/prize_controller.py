from flask import request, jsonify
import datetime
import os
import logging
from main_app.models.admin.prize_model import PrizeDetail, AdminPrizes
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.product_model import Product
from main_app.utils.admin.helpers import generate_prize_uid

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------- Exciting Prizes

UPLOAD_FOLDER ="uploads/prizes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def add_exciting_prizes():
    try:
        logger.info("Add Exciting Prizes API called")
        data = request.get_json()
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        title = data.get("title")
        term_conditions = data.get("term_conditions")
        admin_uid = data.get("admin_uid")
        required_meteors = data.get("required_meteors")
        product_id = data.get("product_uid")
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

        #  Validation fields
        if not all ([title , term_conditions, admin_uid, required_meteors]):
          logger.warning("Missing required fields.")
          return jsonify({"message": "All fields are required"}), 400
        
          # Validate meteors is numeric
        try:
            required_meteors = int(required_meteors)
        except ValueError:
            logger.warning("Invalid required_meteors: must be an integer.")
            return jsonify({"message": "required_meteors must be a number"}), 400

         # Check user found or not 
        if not Admin.objects(admin_uid=admin_uid).first():
            logger.warning(f"Admin not found for UID: {admin_uid}")
            return jsonify({"message": "Admin not found" }), 400
        
        # if not Product.objects(id=product_uid).first():
        #     return jsonify({"message": "Product Id not found"}), 400

          # Fetch existing admin prizes
        admin_prize = AdminPrizes.objects(admin_uid=admin_uid).first()
        updated = False

        if admin_prize:
            # Check if a prize with same title exists → update it
            for prize in admin_prize.prizes:
                if prize.title == title:
                    prize.term_conditions = term_conditions
                    prize.required_meteors = required_meteors
                    prize.product_id = product_id
                    if image:
                        prize.image = image
                    updated = True
                    break

            if updated:
                admin_prize.save()
                msg = "Prize updated successfully"
            else:
                # Add new prize
                new_prize = PrizeDetail(
                    prize_id = generate_prize_uid(admin_uid),
                    title=title,
                    term_conditions=term_conditions,
                    image=image,
                    required_meteors=required_meteors,
                    product_id = product_id
                )
                admin_prize.prizes.append(new_prize)
                admin_prize.save()
                msg = "New prize added to existing admin"
        else:
            # First time prize creation for admin
            new_prize = PrizeDetail(
                prize_id = generate_prize_uid(admin_uid),
                title=title,
                term_conditions=term_conditions,
                image=image,
                required_meteors=required_meteors,
                product_id=product_id
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
        access_token = data.get("mode")
        session_id = data.get("log_alt")

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

        record = AdminPrizes.objects(admin_uid=admin_uid).first()
        if not record:
            logger.warning(f"Prize not found")
            return jsonify({"message": "Prize not found"}), 404
        
        # Check if any prize in the list is eligible
        eligible_prizes = []
        for prize in record.prizes:
            if user_meteors >= prize.required_meteors:
                eligible_prizes.append({
                    "title": prize.title,
                    "required_meteors": prize.required_meteors,
                    "image": prize.image,
                    "term_conditions": prize.term_conditions,
                    "product_id": prize.product_id,
                    "created_at": str(prize.created_at),
                })

        if eligible_prizes:
            return jsonify({
                "eligible": True,
                "message": "User is eligible for some prizes",
                "eligible_prizes": eligible_prizes
            }), 200
        else:
            return jsonify({"eligible": False, "message": "Not enough meteors"}), 200
 
    except Exception as e:
        logger.error(f"Check meteors failed:{str(e)}")
        return jsonify({"error": "Internal server error"}), 500