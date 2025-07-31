from flask import request, jsonify
import os, datetime
import logging
from main_app.models.admin.product_model import Product
from main_app.utils.admin.helpers import generate_product_uid, generate_offer_uid
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.product_offer_model import Offer


# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads/products"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===================================================

# function for date DD/MM/YYYY
def parse_date_flexible(date_str):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime((str(date_str)), fmt)
        except ValueError:
            continue
    return None

# =====================================================

def add_product():
    try:
         logger.info("Add Product API")
         data = request.get_json()
         product_name = data.get("product_name")
         original_amt = data.get("original_amt")
         short_desc = data.get("short_desc")
         reward_type = data.get("reward_type")
         admin_uid = data.get("admin_uid")
         image = data.get("image")
         access_token = data.get("mode")
         session_id = data.get("log_alt")

         exist = Admin.objects(admin_uid=admin_uid).first()

        #  if not exist:
        #      return jsonify({"success": False, "message": "User does not exist"}), 400

        #  if not access_token or not session_id:
        #      return jsonify({"message": "Missing token or session", "success": False}), 400

        #  if exist.access_token != access_token:
        #      return ({"success": False,
        #               "message": "Invalid access token"}), 401

        #  if exist.session_id != session_id:
        #      return ({"success": False,
        #               "message": "Session mismatch or invalid session"}), 403

        #  if hasattr(exist, 'expiry_time') and exist.expiry_time:
        #      if datetime.datetime.now() > exist.expiry_time:
        #          return ({"success": False,
        #                   "message": "Access token has expired",
        #                   "token": "expired"}), 401

         if not all([product_name, original_amt, short_desc, admin_uid]):
             return jsonify({"message": "Missing required fields"}), 400

         try:
            original_amt = float(original_amt)
         except ValueError: 
            return jsonify({"message": "Amount must be numeric"}), 400

         # Save product
         pro_dict =  {
            "product_uid" : generate_product_uid(admin_uid),
            "product_name" : product_name,
            "original_amt" : original_amt,
            "short_desc" : short_desc,
            "image" : image,
            "reward_type" : reward_type
            }

         admin_exist = Product.objects(admin_uid = admin_uid).first()
         if not admin_exist:
            product = Product(
                admin_uid=admin_uid,
                products = [pro_dict]
            )
            product.save()
         else:
            # Check for duplicate product under same admin
            for prod in admin_exist.products:
                if prod.get("product_name") == product_name:
                    return jsonify({"message": "Product already exists for this admin"}), 400


            Product.objects(admin_uid=admin_uid).update(
                push__products = pro_dict
            )
        #     return jsonify({"message" : "Product Added Successfully"})
        #  admin_exist.update(
        #      push__products = pro_dict
        #  )

         logger.info(f"Product saved with ID:")
         return jsonify({"success":"true" , "message": "Product Added Successfully" }), 200

    except Exception as e:
        logger.error(f"Product addition failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


#  --------------------------------------------------------------------------------------------------

# Update Product 

# def update_product(product_uid):
#   try:
#      logger.info(f"Update Product API called for UID: {product_uid}")
#      data = request.get_json()
#      admin_uid = data.get("admin_uid")
#      access_token = data.get("mode")
#      session_id = data.get("log_alt")

#     #  exist = Admin.objects(admin_uid=admin_uid).first()

#     #  if not exist:
#     #      return jsonify({"success": False, "message": "User does not exist"}), 400

#     #  if not access_token or not session_id:
#     #      return jsonify({"message": "Missing token or session", "success": False}), 400

#     #  if exist.access_token != access_token:
#     #      return ({"success": False,
#     #               "message": "Invalid access token"}), 401

#     #  if exist.session_id != session_id:
#     #      return ({"success": False,
#     #               "message": "Session mismatch or invalid session"}), 403

#     #  if hasattr(exist, 'expiry_time') and exist.expiry_time:
#     #      if datetime.datetime.now() > exist.expiry_time:
#     #          return ({"success": False,
#     #                   "message": "Access token has expired",
#     #                   "token": "expired"}), 401

#      if not data or not admin_uid:
#             logger.warning("No fields or files provided in request")
#             return jsonify({"message": "No fields provided for update"}), 400

#      product = Product.objects(admin_uid=admin_uid, products__product_uid=product_uid).first()
#      if not product:
#         logger.warning(f"Product not found for UID: {product_uid}")
#         return jsonify({"message": "Product not found"}), 400
#      print("product", product)
#      for p in product.products:
    
#       if p["product_uid"] == product_uid:
#         logger.info(f"Product updated successfully with UID: {p['product_uid']}")

#      if data.get("product_name"):
#         product.product_name = data.get("product_name")

#      if data.get("original_amt"):
#         product.original_amt = float(data.get("original_amt"))

#      if data.get("short_desc"):
#         product.short_desc = data.get("short_desc")   

#      if data.get("reward_type"):
#         product.reward_type = data.get("reward_type")

#      if data.get("image"):
#          product.image = data.get("image")

#      product.save()
#      logger.info(f"Product updated successfully with UID: {product.product_uid}")
#      return jsonify({"success": "true" , "message": "Product updated", "product_uid": str(product.product_uid)}), 200

#   except Exception as e:
#      logger.error(f"Product update failed : {str(e)}")
#      return jsonify({"errro": "Internal server error"}), 500

def update_product(product_uid):
    try:
        logger.info(f"Update Product API called for UID: {product_uid}")
        data = request.get_json()
        admin_uid = data.get("admin_uid")

        if not data or not admin_uid:
            logger.warning("Missing admin_uid or update fields")
            return jsonify({"message": "Missing required data"}), 400

        # Find document with matching admin and embedded product_uid
        product_doc = Product.objects(admin_uid=admin_uid, products__product_uid=product_uid).first()
        if not product_doc:
            logger.warning(f"Product not found for UID: {product_uid}")
            return jsonify({"message": "Product not found"}), 400

        # Loop through embedded products and update the matching one
        updated = False
        for product in product_doc.products:
            if product.get("product_uid") == product_uid:
                if data.get("product_name"):
                    product["product_name"] = data["product_name"]
                if data.get("original_amt"):
                    try:
                        product["original_amt"] = float(data["original_amt"])
                    except ValueError:
                        return jsonify({"message": "Amount must be numeric"}), 400
                if data.get("short_desc"):
                    product["short_desc"] = data["short_desc"]
                if data.get("reward_type"):
                    product["reward_type"] = data["reward_type"]
                if data.get("image"):
                    product["image"] = data["image"]
                updated = True
                logger.info(f"Product updated successfully with UID: {product_uid}")
                break

        if not updated:
            logger.warning(f"Product with UID {product_uid} not found in list")
            return jsonify({"message": "Product not found"}), 400

        # Save document after editing the embedded product
        product_doc.save()

        return jsonify({
            "success": True,
            "message": "Product updated",
            "product_uid": product_uid
        }), 200

    except Exception as e:
        logger.error(f"Product update failed : {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

# -----------------------------------------------------------------------------------------------------------


def delete_product(product_uid):
    try:
        logger.info(f"Delete Product API called for UID: {product_uid}")
        data = request.get_json()
        admin_uid = data.get("admin_uid")

        if not admin_uid:
            return jsonify({"message": "Missing admin_uid"}), 400

        product_doc = Product.objects(admin_uid=admin_uid, products__product_uid=product_uid).first()
        if not product_doc:
            logger.warning(f"No product found for UID: {product_uid}")
            return jsonify({"message": "Product not found"}), 404

        original_count = len(product_doc.products)
        product_doc.products = [p for p in product_doc.products if p.get("product_uid") != product_uid]

        if len(product_doc.products) == original_count:
            logger.warning("No product matched for deletion")
            return jsonify({"message": "Product not found in list"}), 404

        product_doc.save()
        logger.info(f"Product deleted successfully: {product_uid}")

        return jsonify({"success": True, "message": "Product deleted", "deleted_uid": product_uid}), 200

    except Exception as e:
        logger.error(f"Product deletion failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



# --------------------------------------------------------------------------------------------

# Add Offer

UPLOAD_FOLDER = "uploads/offers"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def add_offer():
 try:
     logger.info("Add Offer API called")
     data = request.get_json()
     offer_name = data.get("offer_name")
     one_liner = data.get("one_liner")
     button_txt = data.get("button_txt")
     off_percent = int(data.get("off_percent", "0"))
     status = data.get("status")
     start_date = parse_date_flexible(data.get("start_date"))
     expiry_date = parse_date_flexible(data.get("expiry_date"))
     product_id = data.get("product_id")
     admin_uid = data.get("admin_uid")
     image = data.get("image")

     if not offer_name and not one_liner and not button_txt and not off_percent and not  start_date and not expiry_date:
         return jsonify({"message": "All fields are required"}), 400

     if not start_date or not expiry_date:
         return jsonify({"message": "Invalid date format (DD/MM/YYYY/ DD-MM-YYYY)"}), 400

    #  try:
    #     off_percent = float(off_percent)
    #  except ValueError:
    #     return jsonify({"message": "off_percent must be numeric"}), 400

    # Determine offer status based on date
     current_date = datetime.datetime.now().date()
     if start_date.date() > current_date:
         status = "Upcoming"
     elif start_date.date() <= current_date <= expiry_date.date():
         status = "Live"
     else:
         status = "Pause"

   # Save product
     off_dic =  {
        "offer_uid": generate_offer_uid(admin_uid),
        "offer_name": offer_name,
        "one_liner": one_liner,
        "image": image,
        "button_txt": button_txt,
        "off_percent": off_percent,
        "status": status,
        "product_uid": product_id,
        # "admin_uid": admin_uid,
        "start_date": start_date,
        "expiry_date": expiry_date
        }

     admin_exist = Offer.objects(admin_uid = admin_uid).first()
     if not admin_exist:
            offer = Offer(
                admin_uid=admin_uid,
                offers = [off_dic]
            )
            offer.save()
            logger.info(f"Offer saved with ID: ")
            return jsonify({"success": True, "message": "Offer add successfully"}), 200

     else:
        Offer.objects(admin_uid=admin_uid).update(
                    push__offers = off_dic
                )

        logger.info(f"Offer saved with ID: ")
        return jsonify({"success": True , "message": "Offer add successfully"}), 200

 except Exception as e:
        logger.error(f"offer failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# --------------------------------------------------------------------------------------------------

# Update Offers

def update_offer():
    try:
        logger.info("Update Offer API called")
        data = request.get_json()
        offer_uid = data.get("offer_uid")
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        start = parse_date_flexible(data.get("start_date"))
        expiry = parse_date_flexible(data.get("expiry_date"))
        product_uid = data.get("product_uid")

        # exist = Admin.objects(admin_uid=admin_uid).first()

        # if not exist:
        #     return jsonify({"success": False, "message": "User does not exist"}), 400

        # if not access_token or not session_id:
        #     return jsonify({"message": "Missing token or session", "success": False}), 400

        # if exist.access_token != access_token:
        #     return ({"success": False,
        #              "message": "Invalid access token"}), 401
        # if exist.session_id != session_id:
        #     return ({"success": False,
        #              "message": "Session mismatch or invalid session"}), 403

        # if hasattr(exist, 'expiry_time') and exist.expiry_time:
        #     if datetime.datetime.now() > exist.expiry_time:
        #         return ({"success": False,
        #                  "message": "Access token has expired",
        #                  "token": "expired"}), 401

        if not data:
            logger.warning("No data or files provided")
            return jsonify({"message": "No fields provided for update"}), 400

        if not offer_uid or not admin_uid:
            logger.warning("Missing offer UID")
            return jsonify({"message": "Offer uid and admin uid not found"}), 400

        offer_doc = Offer.objects(admin_uid=admin_uid).first()
        if not offer_doc:
            logger.warning(f"Offer not found for UID: {offer_uid}")
            return jsonify({"message" : "Offer not found"}), 400
        
        match_offer = None
        for off in offer_doc.offers:
            if off ["offer_uid"] == offer_uid:
                match_offer = off
        if not match_offer:
            return jsonify({"message": "Offer uid not found"}), 400        
        
        if data.get("offer_name"):
         match_offer["offer_name"] = data.get("offer_name")

        if data.get("one_liner"):
         match_offer["one_liner"] = data.get("one_liner")

        if data.get("button_txt"):
         match_offer["button_txt"] = data.get("button_txt")

        if data.get("off_percent"):
          try:
             match_offer["off_percent"] = float(data.get("off_percent"))
          except ValueError:
             return jsonify({"message": "off_percent must be numeric"}), 400

        if data.get("status"):
         match_offer["status"] = data.get("status")

        if "start_date" in data:
            if not start:
                return jsonify({"message": "Invalid start_date format"}), 400
            match_offer["start_date"] = start

        if "expiry_date" in data:
            if not expiry:
                return jsonify({"message": "Invalid expiry_date format"}), 400
            match_offer["expiry_date"] = expiry

         #  Determine offer status based on date
        current_date = datetime.datetime.now().date()
        if start.date() > current_date:
           match_offer["status"] = "Upcoming"
        elif start.date() <= current_date <= expiry.date():
           match_offer["status"] = "Live"
        else:
          match_offer["status"] = "Pause"

        offer_doc.save()

        logger.info(f"Offer updated successfully for product UID: {offer_uid}")
        return jsonify({"success": "true" , "message": "Offer updated successfully"}), 200

    except Exception as e:
        logger.error(f"offer updated failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
