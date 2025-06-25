from flask import request, jsonify
from werkzeug.utils import secure_filename
import os, datetime
from main_app.models.admin.add_product_model import AddProduct
import logging

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads/products"


# function for date DD/MM/YYYY
def parse_date_flexible(date_str):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


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

        #  if not all((product_name, original_amt, discounted_amt, short_desc)):
        #      return jsonify({"error": "Missing required fields"}), 400
         required_fields = {
             "product_name": product_name,
             "original_amt": original_amt,
             "discounted_amt": discounted_amt,
             "short_desc": short_desc
             }
         missing = [key for key, val in required_fields.items() if not val]
         if missing:
           return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
      
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
       
        #  image_url = r"C:\Users\hp-\OneDrive\Pictures\Screenshots\Screenshot 2025-06-11 115415.png"
        #  image = request.files.get("image")
        #  if image:
        #     filename = secure_filename(image.filename)
        #     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        #     image_path = os.path.join(UPLOAD_FOLDER, filename)
        #     image.save(image_path)
        #     image_url = image_path
    
          # Save product
         product = AddProduct(
            product_name=product_name,
            original_amt=original_amt,
            discounted_amt=discounted_amt,
            short_desc=short_desc,
            # image_url=image_url,
            reward_type=reward_type,
            status=status,
            visibility_till=visibility_date
        )
         product.save()

         logger.info(f"Product saved with ID: {product.id}")
         return jsonify({"message": "Product added", "id": str(product.id)}), 200

    except Exception as e:
        logger.error(f"Product addition failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
