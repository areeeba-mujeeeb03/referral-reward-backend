from flask import request, jsonify
import datetime
from main_app.models.admin.discount_coupon_model import ProductDiscounts, DiscountCoupon
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
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        offer_title = data.get('offer_title')
        offer_desc  =data.get('offer_desc')
        tag = data.get('tag')
        start_date = parse_date_flexible(data.get('start_date'))
        start_time = data.get('start_time')
        end_date = parse_date_flexible(data.get('end_date'))
        end_time = data.get('end_time')
        offer_code = data.get('code')
        pop_up_text = data.get('pop_up_text')

        admin = Admin.objects(admin_uid=admin_uid).first()

        if not admin:
            logger.info("attempt with Unauthorized user_id")
            return jsonify({"success": False, "message": "User does not exist"})

        # if not access_token or not session_id:
        #     logger.info("attempt with Missing token or session in request body")
        #     return jsonify({"message": "Missing token or session", "success": False}), 400
        #
        # if admin.access_token != access_token:
        #     logger.info("attempt with Invalid access token")
        #     return ({"success": False,
        #              "message": "Invalid access token"}), 401
        #
        # if admin.session_id != session_id:
        #     logger.info("Session mismatch or invalid session")
        #     return ({"success": False,
        #              "message": "Session mismatch or invalid session"}), 403
        #
        # if hasattr(admin, 'expiry_time') and admin.expiry_time:
        #     logger.info("Access Token has expired")
        #     if datetime.datetime.now() > admin.expiry_time:
        #         return ({"success": False,
        #                  "message": "Access token has expired",
        #                  "token": "expired"}), 401

        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time_obj = datetime.datetime.strptime(end_time, "%H:%M").time()

        start_timestamp = datetime.datetime.combine(start_date, start_time_obj)
        expiry_timestamp = datetime.datetime.combine(end_date, end_time_obj)

        if not all([offer_code, offer_desc, offer_title,start_date,end_date,pop_up_text, tag]):
            return jsonify({"error": "All fields are required"}), 400

        data_dict = {"offer_title": offer_title,
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
                     "active": "False"
                     }

        special = Offer.objects(admin_uid=admin_uid).first()

        for offer in special.special_offer:
            if offer['active'] == "True":
                return jsonify({"message": "You cannot add offer as one special offer is already active"}), 400

        if special:
            Offer.objects(admin_uid=admin_uid).update(
                    push__special_offer=data_dict
            )

        if not special:
            add = Offer(
                admin_uid = admin_uid,
                special_offer = []
            )
            add.save()

            if start_timestamp > datetime.datetime.now():
                data_dict['active'] = "True"
            Offer.objects(admin_uid = admin_uid).update(
                push__special_offer=data_dict
            )

            return jsonify({"message": "Special Offer Added"}), 201
        return jsonify({"message": "Something went wrong"}), 201


    except Exception as e:
        logger.error(f"Failed to add Special offer as {str(e)}")
        return jsonify({"message": "Something Went Wrong"}), 500