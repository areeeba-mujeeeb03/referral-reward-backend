from flask import request, jsonify
import os, datetime, logging
from bson import ObjectId
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.notification_model import PushNotification


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------Add Push Notification

def create_push_notification():
    try:
        logger.info(f"Add push notification API called:")
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        program_id = data.get("program_id")
        title = data.get("title")
        message = data.get("message")
        button_text = data.get("button_text")
        button_url = data.get("button_url")
        # segment = data.get("segment", "All")
        # specific_users = data.get("specific_users", [])
        notification_type = data.get("notification_type")
        date_str = data.get("date")  # Format: DD/MM/YYYY or DD-MM-YYYY
        time_str = data.get("time")  # Format: HH:MM (24h)

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

        if not all([admin_uid, title, message]):
            return jsonify({"error": "Missing required fields"}), 400

        # Parse datetime
        if date_str and time_str:
            try:
                combined = f"{date_str} {time_str}"
                schedule_date = datetime.datetime.strptime(combined, "%d/%m/%Y %H:%M")
            except:
                return jsonify({"error": "Invalid date or time format"}), 400
        else:
            schedule_date = datetime.datetime.now()
        n_id = generate_notification_uid(admin_uid)

        notification_doc = PushNotification.objects(admin_uid=admin_uid, program_id=program_id).first()
        notification_data = {
            "notification_id": n_id,
            "title": title,
            "message": message,
            "button_text": button_text,
            "button_url": button_url,
            "notification_type": notification_type,
            "schedule_date": schedule_date
        }

        if notification_doc:
            # Append to existing document
            notification_doc.all_notifications.append(notification_data)
            notification_doc.save()
        else:
            # Create new document
            new_notification = PushNotification(
                admin_uid=admin_uid,
                program_id=program_id,
                all_notifications=[notification_data]
            )
            new_notification.save()
     
        logger.info(f"Push notification saved")
        return jsonify({"success": True, "message": "Notification created successfully"}), 200

    except Exception as e:
         logger.error(f"Push notification failed: {str(e)}")
         return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------------------

# ----------- List of push notification

def list_push_notifications():
    try:
        logger.info(f"List push notification API called:")
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        program_id = data.get("program_id")
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
            
        if not admin_uid:
            return jsonify({"error": "Missing admin_uid"}), 400

        notifications = PushNotification.objects(admin_uid=admin_uid, program_id = program_id).order_by('-created_at')
        print(notifications)
        result = []

        # for n in notifications:
        #     no = n.to_mongo().to_dict()
        #     result.append(no)
        # print(result)
        for n in notifications:
            no = n.to_mongo().to_dict()
            no['_id'] = str(no['_id'])  # Convert ObjectId to string
            if 'schedule_date' in no and isinstance(no['schedule_date'], datetime.datetime):
                no['schedule_date'] = no['schedule_date'].isoformat()  # Convert datetime to string
            result.append(no)

        return jsonify({"success": True,
                        "notifications": result}), 200

    except Exception as e:
        logger.error(f"list push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------

#------- Update notification

# def update_push_notification(notification_id):
#     try:
#         data = request.get_json()
#         admin_uid = data.get("admin_uid")
#         access_token = data.get("mode")
#         session_id = data.get("log_alt")
#         program_id = data.get("program_id")
#         exist = Admin.objects(admin_uid=admin_uid).first()

#         # if not exist:
#         #     return jsonify({"success": False, "message": "User does not exist"}), 400

#         # if not access_token or not session_id:
#         #     return jsonify({"message": "Missing token or session", "success": False}), 400

#         # if exist.access_token != access_token:
#         #     return ({"success": False,
#         #              "message": "Invalid access token"}), 401

#         # if exist.session_id != session_id:
#         #     return ({"success": False,
#         #              "message": "Session mismatch or invalid session"}), 403

#         # if hasattr(exist, 'expiry_time') and exist.expiry_time:
#         #     if datetime.datetime.now() > exist.expiry_time:
#         #         return ({"success": False,
#         #                  "message": "Access token has expired",
#         #                  "token": "expired"}), 401

#         notification = PushNotification.objects(notification_id=notification_id).first()
#         if not notification:
#             return jsonify({"error": "Notification not found"}), 404
        
        
#         if not data:
#             logger.warning("No fields or files provided in request")
#             return jsonify({"message": "No fields provided for update"}), 400
        

#         for field in ["title", "message", "button_text", "button_url"]:
#             if field in data:
#                 setattr(notification, field, data[field])
            
#         date_str = data.get("date")
#         time_str = data.get("time")
#         if date_str and time_str:
#             try:
#                 combined = f"{date_str} {time_str}"
#                 notification.schedule_date = datetime.datetime.strptime(combined, "%d/%m/%Y %H:%M")
#             except ValueError:
#                 return jsonify({"error": "Invalid date/time format"}), 400
            
   
     
#         notification.save()
#         logger.info(f"Update push notification saved")
#         return jsonify({"success": True, "message": "Notification updated"}), 200

#     except Exception as e:
#         logger.error(f"Update push notification failed: {str(e)}")
#         return jsonify({"error": "Internal server error"}), 500


def update_push_notification(notification_id):
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        program_id = data.get("program_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
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

        if not admin_uid  or not notification_id:
            return jsonify({"error": "Missing required fields"}), 400

        # Step 1: Find the main PushNotification document
        notification_doc = PushNotification.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not notification_doc:
            return jsonify({"error": "Notification document not found"}), 404

        # Step 2: Find the specific notification inside all_notifications
        found = False
        for item in notification_doc.all_notifications:
            if item.get("notification_id") == notification_id:
                # Step 3: Update allowed fields
                for field in ["title", "message", "button_text", "button_url", "date", "time"]:
                    if field in data:
                        item[field] = data[field]

                date_str = data.get("date")
                time_str = data.get("time")
                if date_str and time_str:
                    try:
                        combined = f"{date_str} {time_str}"
                        item["schedule_date"] = datetime.datetime.strptime(combined, "%d/%m/%Y %H:%M")
                    except ValueError:
                        return jsonify({"error": "Invalid date/time format"}), 400

                found = True
                break

        if not found:
            return jsonify({"error": "Notification ID not found in document"}), 404

        # Step 4: Save the document
        notification_doc.save()
        logger.info("Push notification updated successfully")
        return jsonify({"success": True, "message": "Notification updated"}), 200

    except Exception as e:
        logger.error(f"Update push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
  



# ----------------------------------------------------------

# Delete notification 

def delete_push_notification(notification_id):
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
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
        
        if not admin_uid  or not notification_id:
            return jsonify({"error": "Missing required fields"}), 400
        
         # Step 1: Find the PushNotification document
        notification_doc = PushNotification.objects(admin_uid=admin_uid).first()
        if not notification_doc:
            return jsonify({"error": "Notification document not found"}), 404

        # Step 2: Find and remove the specific notification from all_notifications
        original_count = len(notification_doc.all_notifications)
        notification_doc.all_notifications = [
            n for n in notification_doc.all_notifications if n.get("notification_id") != notification_id
        ]

        if len(notification_doc.all_notifications) == original_count:
            return jsonify({"error": "Notification ID not found"}), 404

        # Step 3: Save the updated document
        notification_doc.save()
        logger.info("Notification deleted successfully")
        return jsonify({"success": True, "message": "Notification deleted"}), 200


    #     # Step 1: Find the main PushNotification document
    #     notification_doc = PushNotification.objects(admin_uid=admin_uid).first()
    #     if not notification_doc:
    #         return jsonify({"error": "Notification document not found"}), 404

    #     notification = PushNotification.objects(notification_id=notification_id).first()
    #     if not notification:
    #         return jsonify({"error": "Notification not found"}), 400

    #     notification.delete()
    #     logger.info(f"Delete push notification")
    #     return jsonify({"success": True, "message": "Notification deleted"}), 200

    except Exception as e:
        logger.error(f"Delete push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500



# =======================

# Get Push Notification

# =======================


def get_notification(notification_id):
    try:
        # Extract auth info from query parameters
        admin_uid = request.args.get("admin_uid")
        program_id = request.args.get("program_id")
        access_token = request.args.get("mode")
        session_id = request.args.get("log_alt")

        ## Validation
        if not admin_uid or not access_token or not session_id:
            return jsonify({"message": "Missing credentials", "success": False}), 400

        # Find admin
        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        if admin.access_token != access_token:
            return jsonify({"success": False, "message": "Invalid access token"}), 401

        if admin.session_id != session_id:
            return jsonify({"success": False, "message": "Invalid session"}), 403

        if hasattr(admin, 'expiry_time') and admin.expiry_time:
            if datetime.datetime.now() > admin.expiry_time:
                return jsonify({"success": False, "message": "Access token has expired"}), 401
     
        if not admin_uid :
            return jsonify({"success": False, "message": "Missing admin_uid "}), 400

        notification_doc = PushNotification.objects(admin_uid=admin_uid).first()

        if not notification_doc:
            return jsonify({"success": False, "message": "No notifications found"}), 404

        # Search inside all_notifications
        for notif in notification_doc.all_notifications:
            if notif["notification_id"] == notification_id:
                return jsonify({
                    "success": True,
                    "notification": {
                        "notification_id": notif["notification_id"],
                        "title": notif.get("title"),
                        "message": notif.get("message"),
                        "button_text": notif.get("button_text"),
                        "button_url": notif.get("button_url"),
                        "notification_type": notif.get("notification_type"),
                        "schedule_date": notif.get("schedule_date").strftime("%d/%m/%Y %H:%M") if notif.get("schedule_date") else None
                    }
                }), 200

        return jsonify({
            "success": False,
            "message": "Notifications not found"
        }), 400 

    except Exception as e:
        logger.error(f"Fetch push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
       




def generate_notification_uid(admin_uid):
    count = PushNotification.objects(admin_uid=admin_uid).count() + 1
    return f"NOTI_{str(count).zfill(2)}"