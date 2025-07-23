from flask import request, jsonify
import os, datetime
import logging
from main_app.models.admin.product_model import Product
from main_app.utils.admin.helpers import generate_product_uid, generate_offer_uid
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.product_offer_model import ProductOffer


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

         # if not exist:
         #     return jsonify({"success": False, "message": "User does not exist"})
         #
         # if not access_token or not session_id:
         #     return jsonify({"message": "Missing token or session", "success": False}), 400
         #
         # if exist.access_token != access_token:
         #     return ({"success": False,
         #              "message": "Invalid access token"}), 401
         #
         # if exist.session_id != session_id:
         #     return ({"success": False,
         #              "message": "Session mismatch or invalid session"}), 403
         #
         # if hasattr(exist, 'expiry_time') and exist.expiry_time:
         #     if datetime.datetime.now() > exist.expiry_time:
         #         return ({"success": False,
         #                  "message": "Access token has expired",
         #                  "token": "expired"}), 401

         if not all([product_name, original_amt, short_desc, admin_uid]):
             logger.warning(f"Missing required fields")
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

def update_product(product_uid):
  try:
     logger.info(f"Update Product API called for UID: {product_uid}")
     data = request.get_json()
     admin_uid = data.get("admin_uid")
     access_token = data.get("mode")
     session_id = data.get("log_alt")

     exist = Admin.objects(admin_uid=admin_uid).first()

    #  if not exist:
    #      return jsonify({"success": False, "message": "User does not exist"})

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

     if not data:
            logger.warning("No fields or files provided in request")
            return jsonify({"message": "No fields provided for update"}), 400

     product_doc = Product.objects(admin_uid=admin_uid, products__product_uid=product_uid).first()
     if not product_doc:
        logger.warning(f"Product not found for UID: {product_uid}")
        return jsonify({"message": "Product not found"}), 400
     
     updated = False
     for prod in product_doc.products:
            if prod.get("product_uid") == product_uid:
                if data.get("product_name"):
                    prod["product_name"] = data.get("product_name")
                    updated = True
                if data.get("original_amt"):
                    try:
                        prod["original_amt"] = float(data.get("original_amt"))
                        updated = True
                    except ValueError:
                        return jsonify({"message": "Amount must be numeric"}), 400
                if data.get("short_desc"):
                    prod["short_desc"] = data.get("short_desc")
                    updated = True
                if data.get("reward_type"):
                    prod["reward_type"] = data.get("reward_type")
                    updated = True
                if data.get("image"):
                    prod["image"] = data.get("image")
                    updated = True

     if updated:
            product_doc.save()
            logger.info(f"Product updated successfully with UID: {product_uid}")
            return jsonify({"success": "true", "message": "Product updated", "uid": product_uid}), 200
     else:
            return jsonify({"message": "No valid fields to update"}), 400

  except Exception as e:
     logger.error(f"Product update failed : {str(e)}")
     return jsonify({"errro": "Internal server error"}), 500

    #  if data.get("product_name"):
    #     product_doc.product_name = data.get("product_name")

    #  if data.get("original_amt"):
    #     product_doc.original_amt = float(data.get("original_amt"))

    #  if data.get("short_desc"):
    #     product_doc.short_desc = data.get("short_desc")   

    #  if data.get("reward_type"):
    #     product_doc.reward_type = data.get("reward_type")

    #  if data.get("image"):
    #      product_doc.image = data.get("image")

    #  product_doc.save()
    #  logger.info(f"Product updated successfully with UID: {product_doc.product_uid}")
    #  return jsonify({"success": "true" , "message": "Product updated", "uid": str(product_doc.product_uid)}), 200






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

     if not all ([offer_name, one_liner, button_txt, off_percent, start_date, expiry_date, admin_uid, product_id]):
         logger.warning(f"All fields are required")
         return jsonify({"message": "All fields are required"}), 400

     if not start_date or not expiry_date:
         return jsonify({"message": "Invalid date format (DD/MM/YYYY/ or DD-MM-YYYY)"}), 400

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
        "product_id": product_id,
        # "admin_uid": admin_uid,
        "start_date": start_date,
        "expiry_date": expiry_date
        }
         
     admin_exist = ProductOffer.objects(admin_uid = admin_uid).first()
     if not admin_exist:
            offer = ProductOffer(
                admin_uid=admin_uid,
                offers = [off_dic]
            )
            offer.save()
            return jsonify({"success": True , "message": "Offer add successfully"}), 200
    #  else:
    #     # Check for duplicate product under same admin
    #     for off in admin_exist.offers:
    #         if off.get("offer_name") == offer_name:
    #             return jsonify({"message": "offer already exists for this admin"}), 400

     else:
        ProductOffer.objects(admin_uid=admin_uid).update(push__offers = off_dic)

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
        uid = data.get("uid")

        exist = Admin.objects(admin_uid=admin_uid).first()

        # if not exist:
        #     return jsonify({"success": False, "message": "User does not exist"})

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
        
        offer_doc = ProductOffer.objects(admin_uid=admin_uid).first()
        if not offer_doc:
            return jsonify({"message": "Admin not found"}), 404

        # Find the specific embedded offer
        for offer in offer_doc.offers:
            if offer.get("offer_uid") == offer_uid:
                if data.get("offer_name"):
                    offer["offer_name"] = data.get("offer_name")

                if data.get("one_liner"):
                    offer["one_liner"] = data.get("one_liner")

                if data.get("button_txt"):
                    offer["button_txt"] = data.get("button_txt")

                if data.get("off_percent"):
                    try:
                        offer["off_percent"] = float(data.get("off_percent"))
                    except ValueError:
                        return jsonify({"message": "off_percent must be numeric"}), 400

                if "start_date" in data:
                    start = parse_date_flexible(data.get("start_date"))
                    if not start:
                        return jsonify({"message": "Invalid start_date format"}), 400
                    offer["start_date"] = start
                else:
                    start = offer.get("start_date")

                if "expiry_date" in data:
                    expiry = parse_date_flexible(data.get("expiry_date"))
                    if not expiry:
                        return jsonify({"message": "Invalid expiry_date format"}), 400
                    offer["expiry_date"] = expiry
                else:
                    expiry = offer.get("expiry_date")

                # Update status based on date
                current_date = datetime.datetime.now().date()
                if start.date() > current_date:
                    offer["status"] = "Upcoming"
                elif start.date() <= current_date <= expiry.date():
                    offer["status"] = "Live"
                else:
                    offer["status"] = "Pause"

                # Save the document
                offer_doc.save()
                logger.info(f"Offer updated successfully for UID: {offer_uid}")
                return jsonify({"success": True, "message": "Offer updated successfully"}), 200

        return jsonify({"message": "Offer not found for given offer UID"}), 404

    except Exception as e:
        logger.error(f"offer updated failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


        # offer = Offer.objects(admin_uid=admin_uid, offers__offer_uid=offer_uid).first()
        # if not offer:
        #     logger.warning(f"Product not found for UID: {offer_uid}")
        #     return jsonify({"message" : "Product not found"}), 400
        
        # if data.get("offer_name"):
        #  offer.offer_name = data.get("offer_name")

        # if data.get("one_liner"):
        #  offer["one_liner"] = data.get("one_liner")

        # if data.get("button_txt"):
        #  offer.button_txt = data.get("button_txt")

        # if data.get("off_percent"):
        #   try:
        #      offer.off_percent = float(data.get("off_percent"))
        #   except ValueError:
        #      return jsonify({"message": "off_percent must be numeric"}), 400

        # if data.get("status"):
        #  offer.status = data.get("status")

        # if "start_date" in data:
        #     start = parse_date_flexible(data.get("start_date"))
        #     if not start:
        #         return jsonify({"message": "Invalid start_date format"}), 400
        #     offer.start_date = start

        # if "expiry_date" in data:
        #     expiry = parse_date_flexible(data.get("expiry_date"))
        #     if not expiry:
        #         return jsonify({"message": "Invalid expiry_date format"}), 400
        #     offer.expiry_date = expiry

        #  #  Determine offer status based on date
        # current_date = datetime.datetime.now().date()
        # if start.date() > current_date:
        #    offer.status = "Upcoming"
        # elif start.date() <= current_date <= expiry.date():
        #    offer.status = "Live"
        # else:
        #   offer.status = "Pause"

        # offer.save()

        # logger.info(f"Offer updated successfully for product UID: {offer_uid}")
        # return jsonify({"success": "true" , "message": "Offer updated successfully"}), 200
