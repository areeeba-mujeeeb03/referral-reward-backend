
from flask import request, jsonify
from werkzeug.utils import secure_filename
import os, datetime
import logging
from main_app.models.admin.add_product_model import Product
from main_app.utils.admin.helpers import generate_product_uid, generate_offer_uid
# from main_app.models.admin.product_offer_model import Offer

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
         
         data = request.form
         product_name = data.get("product_name")
         original_amt = data.get("original_amt")
         discounted_amt = data.get("discounted_amt")
         short_desc = data.get("short_desc")
         reward_type = data.get("reward_type", "")
         status = data.get("status", "Live")
         visibility_till = data.get("visibility_till")
         apply_offer = data.get("apply_offer", "").lower() == "true"

         if not all([product_name, original_amt, discounted_amt, short_desc]):
             return jsonify({"error": "Missing required fields"}), 400
      
         try:
            original_amt = float(original_amt)
            discounted_amt = float(discounted_amt)
         except ValueError: 
            return jsonify({"error": "Amount must be numeric"}), 400
    
          # Convert date
         visibility_date = None
         if visibility_till:
            visibility_date = parse_date_flexible(visibility_till)
            if not visibility_date:
                return jsonify({"error": "Date must be in DD/MM/YYYY or DD-MM-YYYY format"}), 400
       
          # Image upload
            image = request.files.get("image")
            image_url = ""
            if not image:
               return jsonify({"error": "No image uploaded"}), 400
         
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = f"/{image_path}"            
            

         offer_data = {}
         if apply_offer:
            offer_name = data.get("offer_name")
            one_liner = data.get("one_liner")
            button_txt = data.get("button_txt")
            off_percent = data.get("off_percent")
            start_date = data.get("start_date")
            expiry_date = data.get("expiry_date")
            offer_type = data.get("offer_type")

            if not all([offer_name, one_liner, button_txt, off_percent, start_date, expiry_date, offer_type]):
                return jsonify({"error": "Missing offer fields"}), 400

            try:
                off_percent = float(off_percent)
            except ValueError:
                return jsonify({"error": "off_percent must be numeric"}), 400

            start_date_parsed = parse_date_flexible(start_date)
            expiry_date_parsed = parse_date_flexible(expiry_date)

            if not start_date_parsed or not expiry_date_parsed:
                return jsonify({"error": "Invalid offer date format"}), 400

            #  Determine offer status based on date
            current_date = datetime.datetime.now().date()
            if start_date_parsed.date() > current_date:
                offer_status = "Upcoming"
            else:
                offer_status = "Live"

            offer_data = {
                "offer_name": offer_name,
                "one_liner": one_liner,
                "button_txt": button_txt,
                "off_percent": off_percent,
                "start_date": start_date_parsed,
                "expiry_date": expiry_date_parsed,
                "offer_type":offer_type,
                "offer_status": offer_status
            }

         # Save product
         product = Product(
             uid=generate_product_uid(),
             product_name=product_name,
             original_amt=original_amt,
             discounted_amt=discounted_amt,
             short_desc=short_desc,
             image_url=image_url,
             reward_type=reward_type,
             status=status,
             visibility_till=visibility_date,
             apply_offer=apply_offer,
             **offer_data
         )
         product.save()

         logger.info(f"Product saved with ID: {product.uid}")
         return jsonify({"success":"true" , "message": "Product added successfully", "uid": str(product.uid)}), 200

    except Exception as e:
        logger.error(f"Product addition failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



#  --------------------------------------------------------------------------------------------------

# Update Product 

def update_product(uid):
  try:
     logger.info(f"Update Product API called for UID: {uid}")
     data = request.form

     if not data and not request.files:
            return jsonify({"error": "No fields provided for update"}), 400

     product = Product.objects(uid=uid).first()
     if not product:
        return jsonify({"error": "Product not found"}), 400
     if data.get("product_name"):
        product.product_name = data.get("product_name")

     if data.get("original_amt"):
        product.original_amt = float(data.get("original_amt"))

     if data.get("discounted_amt"):
        product.discounted_amt = float(data.get("discounted_amt")) 

     if data.get("short_desc"):
        product.short_desc = data.get("short_desc")   

     if data.get("reward_type"):
        product.reward_type = data.get("reward_type") 

     if data.get("status"):
        product.status = data.get("status") 

     if data.get("visibility_till"):
        visibility_date = parse_date_flexible(data.get("visibility_till"))
        if not visibility_date:
                return jsonify({"error": "Invalid date format (use DD/MM/YYYY or DD-MM-YYYY)"}),
        product.visibility_till = visibility_date  

     image = request.files.get("image")
     if image:
        filename = secure_filename(image.filename)
        image_path  = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)
        product.image_url = f"/{image_path}"

     product.save()
     print("product", product)

     logger.info(f"Product updated: {product.uid}")
     return jsonify({"success": "true" , "message": "Product updated", "uid": str(product.uid)}), 200

  except Exception as e:
     logger.error(f"Product update failed : {str(e)}")
     return jsonify({"errro": "Internal server error"}), 500


# --------------------------------------------------------------------------------------------------

# # Add Offer

# UPLOAD_FOLDER = "uploads/offers"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# def create_offer():
#  try:
#      logger.info("Add Offer API called")
#      data = request.form
#      offer_name = data.get("offer_name").strip()
#      one_liner = data.get("one_liner").strip()
#      button_txt = data.get("button_txt").strip()
#      off_percent = int(data.get("off_percent", "0"))
#      start_date = parse_date_flexible(data.get("start_date", ""))
#      expiry_date = parse_date_flexible(data.get("expiry_date", ""))

#      if not all([offer_name, one_liner, button_txt, off_percent, start_date, expiry_date]):
#          return jsonify({"error": "All fields are required"}), 400

#      if not start_date or not expiry_date:
#             return jsonify({"error": "Invalid date format (DD/MM/YYYY/ DD-MM-YYYY)"}), 400

#      file = request.files.get("image")
#      if not file:
#         return jsonify({"error": "No image uploaded"}), 400

#      filename = secure_filename(file.filename)
#      image_path = os.path.join(UPLOAD_FOLDER, filename)
#      file.save(image_path)
#      image_url = f"/{image_path}"

#      offer = Offer(
#         offer_uid = generate_offer_uid(),
#         offer_name = offer_name,
#         one_liner = one_liner,
#         image_url = image_url,
#         button_txt = button_txt,
#         off_percent = off_percent,
#         start_date = start_date,
#         expiry_date = expiry_date
#       )

#      offer.save()

#      logger.info(f"Offer saved with ID: {offer.offer_uid}")
#      return jsonify({"message": "Offer add successfully", "offer_id": str(offer.offer_uid)}), 200

#  except Exception as e:
#           logger.error(f"Offer addition failed: {str(e)}")
#           return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------------------------

# Update Offers
def update_offer():
    try:
        logger = logging.getLogger(__name__)
        data = request.form

        uid = data.get("uid")

        if not data and not request.files:
            return jsonify({"error": "No fields provided for update"}), 400

        if not uid:
            return jsonify({"error": "Product uid not found"}), 400

        product = Product.objects(uid=uid).first()
        if not product:
            return jsonify({"error" : "Product not found"}), 400

        apply_offer = data.get("apply_offer", "").lower() == "true"
        product.apply_offer = apply_offer

        # Validation for field updates
        if apply_offer:
            offer_fields = ["offer_name", "one_liner", "button_txt", "off_percent", "start_date", "expiry_date", "offer_type"]
            if not any(field in data for field in offer_fields):
              return jsonify({"error": "No offer fields provided for update"}), 400

            if "apply_offer" in data:
                product.apply_offer = data.get("apply_offer", "").lower() == "true"

            if "offer_name" in data:
                product.offer_name = data.get("offer_name")

            if "one_liner" in data:
                product.one_liner = data.get("one_liner")

            if "button_txt" in data:
                product.button_txt = data.get("button_txt")

            if "off_percent" in data:
                try:
                    product.off_percent = float(data.get("off_percent"))
                except ValueError:
                    return jsonify({"error": "off_percent must be numeric"}), 400

            if "start_date" in data:
                start = parse_date_flexible(data.get("start_date"))
                if not start:
                    return jsonify({"error": "Invalid start_date format"}), 400
                product.start_date = start

            if "expiry_date" in data:
                expiry = parse_date_flexible(data.get("expiry_date"))
                if not expiry:
                    return jsonify({"error": "Invalid expiry_date format"}), 400
                product.expiry_date = expiry

            if "offer_type" in data:
                product.offer_name = data.get("offer_name")

            product.save()
            return jsonify({"success": "true" , "message": "Offer updated successfully"}), 200

        else:
            # product.save()
            return jsonify({"error": "Offer not updated because apply_offer is false"}), 400

    except Exception as e:
        logger.error(f"offer updated failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500










    

