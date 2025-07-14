from flask import request , jsonify
import os
import logging
# from werkzeug.utils import secure_filename
from main_app.models.admin.how_it_work_model import HowItWork 
from main_app.models.admin.advertisment_card_model import AdvertisementCardItem, AdminAdvertisementCard
from main_app.models.admin.admin_model import Admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_how_it_work():
    try:
        logger.info(f"Add and update how it work API called for uid:")
        data = request.get_json()
        
        title1 = data.get("title1")
        desc1 = data.get("desc1")
        title2 = data.get("title2")
        desc2 = data.get("desc2")
        title3 = data.get("title3")
        desc3 = data.get("desc3")
        admin_uid = data.get("admin_uid")
        
        if not data:
            logger.warning("No data received in request")
            return jsonify({"message": "No fields provided"}), 400

        # Validaiton
        if not all([admin_uid, title1, desc1, title2, desc2, title3, desc3 ]):
           logger.warning("Missing required fields")
           return jsonify({"message": " All fields are required."}), 400
        
        # Check user found or not 
        if not Admin.objects(admin_uid=admin_uid).first():
            logger.warning(f"Admin not found for UID: {admin_uid}")
            return jsonify({"message": "Admin not found" }), 400
         
        # Check if document exists
        existing = HowItWork.objects(admin_uid=admin_uid).first()
        if existing:
            fields_changed = False
           
            if title1 != existing.title1:
                 fields_changed = True
          
            if desc1 != existing.desc1:
                 fields_changed = True     
            
            if title1 != existing.title1:
                 fields_changed = True
            
            if desc2 != existing.desc2:
                 fields_changed = True
           
            if title1 != existing.title1:
                 fields_changed = True
            
            if desc3 != existing.desc3:
                 fields_changed = True
            
            if not fields_changed:
                return jsonify({"message": "No fields updated"})
         
          # Perform update
            update_data = {
                "title1": title1,
                "desc1":desc1,
                "title2":title2,
                "desc2":desc2,
                "title3":title3,
                "desc3":desc3
                }

            existing.update(**update_data)
            logger.info(f"'How It Work' updated successfully for UID: {admin_uid}")
            msg = "Updated successfully"
        else:
            HowItWork(**data).save()
            logger.info(f"'How It Work' added successfully for UID: {admin_uid}")
            msg = "Added successfully"

        logger.info(f"How it work saved with ID")
        return jsonify({"success": "true" ,"message": msg}), 200

    except Exception as e:
        logger.error(f"how it work failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ------------------------------------------------------------------------------------------------------

# Advertisement card

UPLOAD_FOLDER = "uploads/advertisement_card"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def advertisement_card():
    try:
      logger.warning(f"Advertisment API called:")
      data = request.form
      
      title = data.get("title")
      description = data.get("description")
      button_txt = data.get("button_txt")
      admin_uid = data.get("admin_uid")
      image = data.get("image")
      
      if not all([title, description, button_txt, admin_uid]):
         logger.warning("Missing required fields")
         return jsonify({"message": "All fields are required."}), 400
      
        # Check user found or not 
      if not Admin.objects(admin_uid=admin_uid).first():
            logger.warning(f"Admin not found for UID: {admin_uid}")
            return jsonify({"message": "Admin not found" }), 400
      
    #    # Image upload
    #   image = request.files.get("image_url")
    #   image_url = None
    #   if image:   
    #     filename = secure_filename(image.filename)
    #     image_path = os.path.join(UPLOAD_FOLDER, filename)
    #     image.save(image_path)
    #     image_url = f"/{image_path}"    

         # Prepare embedded ad card
      ad_card = AdvertisementCardItem(
            title=title,
            description=description,
            button_txt=button_txt,
            image=image
        )

        # Insert or update (append to array)
      record = AdminAdvertisementCard.objects(admin_uid=admin_uid).first()
        
      if record:
            # Check if card with same title exists (Update)
            updated = False
            for card in record.advertisement_cards:
                if card.title == title:
                    card.description = description
                    card.button_txt = button_txt
                    if image:
                        card.image = image
                    updated = True
                    break

            if updated:
                record.save()
                msg = "Advertisement card updated successfully"
            else:
                # Add new card
                new_card = AdvertisementCardItem(
                    title=title,
                    description=description,
                    button_txt=button_txt,
                    image=image,
                )
                record.advertisement_cards.append(new_card)
                record.save()
                msg = "New advertisement card added"
      else:
            # No document found, create new
            new_card = AdvertisementCardItem(
                title=title,
                description=description,
                button_txt=button_txt,
                image=image,
            )
            AdminAdvertisementCard(
                admin_uid=admin_uid,
                advertisement_cards=[new_card]
            ).save()
            msg = "Advertisement card document created and card added"


      logger.info(f"Ad card added for admin UID: {admin_uid}")
      return jsonify({"success": True, "message": msg}), 200
    
    except Exception as e:
       logger.error(f"Add advertisment card failed : {str(e)}")
       return jsonify({"error": "Internal server error"}), 500