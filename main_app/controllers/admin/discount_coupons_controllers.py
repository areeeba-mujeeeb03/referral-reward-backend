from flask import request, jsonify
import datetime
from main_app.models.admin.discount_coupon_model import ProductDiscounts
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.product_model import Product

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_discount_coupons():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        coupon_code = data.get("coupon_code")
        validity_till = data.get("validity_till")
        product_name = data.get("product_name")
        percent = data.get("off_percent")
        desc_text = data.get("desc_text")

        exist = Admin.objects(admin_uid=admin_uid).first()

        if not exist:
            return jsonify({"success": False, "message": "User does not exist"}), 400

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

        if not all([admin_uid, coupon_code]):
            return jsonify({"error": "admin_uid and coupon data are required"}), 400

        product = Product.objects(product_name = product_name).first()
        for pro in product.products:
            if pro['product_name'] == product_name:
                original_amount = pro['original_amt']
                discount_amount = original_amount * percent/100
                now = datetime.datetime.now()
                expiry = now + datetime.timedelta(days=15)
                coupon_data = {"coupon_code" : coupon_code,
                               "product_id" : product.uid,
                               "validity_till" : validity_till,
                               "off_percent" : percent,
                               "discount_amt" : discount_amount,
                               "original_amt" : original_amount,
                               "description" : desc_text,
                               "end_date" : expiry
                               }
                product = ProductDiscounts.objects(admin_uid=admin_uid).first()
                if not product:
                    product = ProductDiscounts(admin_uid=admin_uid, coupons=[])

                for coupon in product.coupons:
                    if coupon['coupon_code'].lower() == coupon_code.lower():
                        return jsonify({"error": "Coupon code already exists"}), 400

                ProductDiscounts.objects(admin_uid=admin_uid).update(
                    push__coupons = coupon_data
                )
                product.save()
                return jsonify({"message": "Discount coupon added successfully"}), 201
    except Exception as e:
        logger.error(f"Failed to add Special offer as {str(e)}")
        return jsonify({"message": "Something Went Wrong"}), 500


def update_discount_coupon():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    coupon_code = data.get("coupon_code")
    updates = data.get("updates")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

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

    if not all([admin_uid, coupon_code, updates]):
        return jsonify({"error": "admin_uid, coupon_code, and updates are required"}), 400

    product_id = updates.get("product_id")
    if not product_id:
        return jsonify({"error": "product_id must be included in updates"}), 400

    product = ProductDiscounts.objects(admin_uid=admin_uid).first()
    if not product:
        return jsonify({"error": "Admin not found"}), 404

    allowed_fields = ["title", "description", "image_url", "start_date", "end_date", "product_id"]
    coupon_code_lower = coupon_code.lower()
    product_id_lower = product_id.lower()

    for coupon in product.coupons:
        if coupon.coupon_code.lower() == coupon_code_lower:
            if coupon.product_id.lower() != product_id_lower:
                return jsonify({"message": "Invalid code for this product"}), 400

            for field in allowed_fields:
                if field in updates:
                    setattr(coupon, field, updates[field])
            product.save()
            return jsonify({"message": "Coupon updated successfully"}), 200

    return jsonify({"error": "Coupon code not found"}), 404


def delete_discount_coupon():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    coupon_code = data.get("coupon_code")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

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

    if not all([admin_uid, coupon_code]):
        return jsonify({"error": "admin_uid and coupon code are required"}), 400

    product_doc = ProductDiscounts.objects(admin_uid=admin_uid).first()
    if not product_doc:
        return jsonify({"error": "Admin not found"}), 404

    for coupon in product_doc.coupons:
        if coupon.coupon_code.lower() == coupon_code.lower():
            product_doc.coupons.remove(coupon)
            product_doc.save()
            return jsonify({"message": "Coupon deleted successfully"}), 200

    return jsonify({"error": "Coupon code not found"}), 404
