import datetime
from flask import request, jsonify
# from werkzeug.utils import secure_filename
from main_app.models.admin.perks_model import ExclusivePerks,Perks,FooterSection, FooterItem
import os , logging
from main_app.models.admin.admin_model import Admin
from main_app.utils.admin.helpers import generate_perks_uid

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads/exclusive_perks"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_exclusive_perks():
     try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        title = data.get("title")
        information = data.get("information")
        term_conditions = data.get("term_conditions")
        image = data.get("image")
        perk_id = data.get("perk_id")

        print(data)

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
        if not all ([title , term_conditions, information, admin_uid]):
                logger.warning("Missing required fields.")
                return jsonify({"message": "All fields are required"}), 400
                
        # Check user found or not 
        if not Admin.objects(admin_uid=admin_uid).first():
            logger.warning(f"Admin not found for UID: {admin_uid}")
            return jsonify({"message": "Admin not found" }), 400
        
        # Check if Perks document exists
        perks_doc = Perks.objects(admin_uid=admin_uid).first()

        if perks_doc:
            updated = False

            # Try to update existing embedded perk by perk_id
            if perk_id:
                for perk in perks_doc.perks:
                    if perk.perk_id == perk_id:
                        perk.title = title
                        perk.information = information
                        perk.term_conditions = term_conditions
                        perk.image = image
                        updated = True
                        message = "Exclusive perk updated successfully"
                        break

            if not updated:
                # Append new perk
                new_perk = ExclusivePerks(
                    perk_id=generate_perks_uid(admin_uid),
                    title=title,
                    information=information,
                    term_conditions=term_conditions,
                    image=image
                )
                perks_doc.perks.append(new_perk)
                message = "Exclusive perk added successfully"

            perks_doc.save()
        else:
            # Create new Perks document with one exclusive perk
            new_perk = ExclusivePerks(
                perk_id=generate_perks_uid(admin_uid),
                title=title,
                information=information,
                term_conditions=term_conditions,
                image=image
            )
            new_doc = Perks(
                admin_uid=admin_uid,
                perks=[new_perk]
            )
            new_doc.save()
            message = "Exclusive perk added successfully"

        return jsonify({"success": True, "message": message}), 200

     except Exception as e:
            logger.error(f"Add exclusive perks failed:{str(e)}")
            return jsonify({"error": "Internal server error"}), 500


        #   # Check if a similar perk exists for the admin
        # existing_perk = ExclusivePerks.objects(admin_uid=admin_uid).first()
        # if existing_perk:
        #     #  existing_perk.update(
        #     #        information=information,
        #     #        term_conditions=term_conditions,
        #     #        image=image
        #     #   )
        #   if existing_perk.perks:
        #     # Update first perk
        #      existing_perk.perks[0].title = title
        #      existing_perk.perks[0].information = information
        #      existing_perk.perks[0].term_conditions = term_conditions
        #      existing_perk.perks[0].image = image
        #      message = "Exclusive perks updated successfully"
        # else:
        #     new_perk = ExclusivePerks(
        #            perk_id = generate_perks_uid(admin_uid),
        #            title=title,
        #            information=information,
        #            term_conditions=term_conditions,
        #            image=image,
        #            admin_uid=admin_uid
        #      )
        #     new_perk.save()
        #     message = "Exclusive perk added successfully"

        # return jsonify({"success": True, "message": message}), 200
    



#----------------------------------------------------------------------------------------

#-------- Footer Section


def edit_footer():
    try:
        logger.info("Update footer API called")
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        content = data.get("content")

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

        if not admin_uid or not content:
            logger.warning("Missing admin_uid or content")
            return jsonify({"message": "Admin uid and content are required"}), 400

        # content = content.strip()
        # if not content:
        #     logger.warning("Empty content after stripping")
        #     return jsonify({"message": "Content cannot be empty"}), 400

        footer_section = FooterSection.objects(admin_uid=admin_uid).first()

        if footer_section:
            # Check for duplicate
            if any(item.content == content for item in footer_section.footer):
                logger.info("Duplicate footer content not added.")
                return jsonify({"message": "Footer already exists"}), 200

            # Append new content
            footer_section.footer.append(FooterItem(content=content))
            footer_section.save()
        else:
            # Create new footer section
            new_footer = FooterSection(
                admin_uid=admin_uid,
                footer=[FooterItem(content=content)]
            )
            new_footer.save()

        logger.info("Footer updated successfully.")
        return jsonify({"message": "Footer updated successfully"}), 200

    except Exception as e:
        logger.exception(f"Update footer failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

