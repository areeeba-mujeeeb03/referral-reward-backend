from flask import request, jsonify
import datetime
from main_app.models.admin.discount_coupon_model import ProductDiscounts
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.special_offer_model import SpecialOffer, Offer
from main_app.controllers.admin.referral_controllers import parse_date_flexible

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_special_offer():
    try:
        data = request.get_json()
        logger.info("Running Special Offer Generation")

        # Extract required data
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")  # Assuming "mode" is being used as access_token
        session_id = data.get("log_alt")
        offer_title = data.get('offer_title')
        offer_desc = data.get('offer_desc')
        tag = data.get('tag')
        start_date = parse_date_flexible(data.get('start_date'))
        start_time = data.get('start_time')
        end_date = parse_date_flexible(data.get('end_date'))
        end_time = data.get('end_time')
        offer_code = data.get('code')
        pop_up_text = data.get('pop_up_text')

        # admin = Admin.objects(admin_uid=admin_uid).first()
        # if not admin:
        #     logger.info(f"Unauthorized access attempt with user_id: {admin_uid}")
        #     return jsonify({"success": False, "message": "User does not exist"}), 401

        # if not access_token or not session_id:
        #     logger.info("Missing token or session in request body")
        #     return jsonify({"message": "Missing token or session", "success": False}), 400
        #
        # if admin.access_token != access_token:
        #     logger.info("Invalid access token")
        #     return jsonify({"success": False, "message": "Invalid access token"}), 401
        #
        # if admin.session_id != session_id:
        #     logger.info("Session mismatch or invalid session")
        #     return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403
        #
        # if hasattr(admin, 'expiry_time') and admin.expiry_time:
        #     if datetime.datetime.now() > admin.expiry_time:
        #         logger.info("Access token has expired")
        #         return jsonify({
        #             "success": False,
        #             "message": "Access token has expired",
        #             "token": "expired"
        #         }), 401

        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.datetime.strptime(end_time, "%H:%M").time()

        start_timestamp = datetime.datetime.combine(start_date, start_time_obj)
        expiry_timestamp = datetime.datetime.combine(end_date, end_time_obj)

        if not all([admin_uid, access_token, session_id,offer_code, offer_desc, offer_title, start_date, end_date, pop_up_text, tag]):
            return jsonify({"error": "All fields are required"}), 400

        if expiry_timestamp <= start_timestamp:
            return jsonify({"error": "End date and time must be after start date and time"}), 400

        offer_data = {
            "offer_title": offer_title,
            "offer_desc": offer_desc,
            "offer_code": offer_code,
            "tag": tag,
            "pop_up_text": pop_up_text,
            "start_date": start_date,
            "end_date": end_date,
            "start_time": start_time,
            "end_time": end_time,
            "start_timestamp": start_timestamp,
            "expiry_timestamp": expiry_timestamp,
            "active": start_timestamp <= datetime.datetime.now()
        }

        existing_offer = Offer.objects(admin_uid=admin_uid).first()

        if existing_offer and existing_offer.special_offer:
            for offer in existing_offer.special_offer:
                if offer['active'] is True:
                    return jsonify({
                        "message": "An active special offer already exists.",
                        "success": False
                    }), 400
                if offer['start_date'] == start_date:
                    return jsonify({
                        "message": "An offer is already scheduled for this date.",
                        "success": False
                    }), 400

        Offer.objects(admin_uid=admin_uid).update_one(
            push__special_offer=offer_data
        )

        logger.info(f"Special offer added successfully for admin: {admin_uid}")
        return jsonify({"message": "Special Offer Added", "success": True}), 201

    except Exception as e:
        logger.error(f"Failed to add Special offer as {str(e)}")
        return jsonify({"message": "Something Went Wrong"}), 500