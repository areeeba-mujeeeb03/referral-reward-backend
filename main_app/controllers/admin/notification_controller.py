from flask import request, jsonify
import os, datetime, logging

from main_app.models.admin.admin_model import Admin
from main_app.models.admin.notification_model import  PushNotification


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
        segment = data.get("segment", "All")
        specific_users = data.get("specific_users", [])
        notification_type = data.get("notification_type")
        date_str = data.get("date")  # Format: DD/MM/YYYY or DD-MM-YYYY
        time_str = data.get("time")  # Format: HH:MM (24h)

        exist = Admin.objects(admin_uid=admin_uid).first()

        if not exist:
            return jsonify({"success": False, "message": "User does not exist"}), 400

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

        notification = PushNotification(
            admin_uid=admin_uid,
            program_id = program_id,
            all_notifications = []
        )
        notification.all_notifications.append({
            "notification_id" : n_id,
            "title" : title,
            "message" : message,
            "button_text" : button_text,
            "button_url" : button_url,
            "segment" : segment,
            "notification_type" : notification_type,
            "specific_users" : [specific_users],
            "schedule_date" : schedule_date
        })
        notification.save()
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

        for n in notifications:
            no = n.to_mongo().to_dict()
            result.append(no)
        print(result)

        return jsonify({"success": True,
                        "notifications": result}), 200

    except Exception as e:
        logger.error(f"list push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------

#------- Update notification

def update_push_notification(notification_id):
    try:
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

        notification = PushNotification.objects(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404
        
        
        if not data and not request.files:
            logger.warning("No fields or files provided in request")
            return jsonify({"message": "No fields provided for update"}), 400

        for field in ["title", "message", "button_text", "button_url", "segment", "specific_users"]:
            if field in data:
                setattr(notification, field, data[field])

        date_str = data.get("date")
        time_str = data.get("time")
        if date_str and time_str:
            try:
                combined = f"{date_str} {time_str}"
                notification.schedule_date = datetime.datetime.strptime(combined, "%d/%m/%Y %H:%M")
            except:
                return jsonify({"error": "Invalid date/time format"}), 400

        notification.save()
        logger.info(f"Update push notification saved")
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
        notification = PushNotification.objects(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 400

        notification.delete()
        logger.info(f"Delete push notification")
        return jsonify({"success": True, "message": "Notification deleted"}), 200

    except Exception as e:
        logger.error(f"Delete push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# =======================

# Get Push Notification

# =======================

def get_push_notification(notification_id):
    try:
        # Extract auth info from query parameters
        admin_uid = request.args.get("admin_uid")
        access_token = request.args.get("mode")
        session_id = request.args.get("log_alt")

        ## Validation
        if not admin_uid or not access_token or not session_id:
            return jsonify({"message": "Missing credentials", "success": False}), 400

        ## Find admin
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

        # Find notification
        notification = PushNotification.objects(id=notification_id).first()
        if not notification:
            return jsonify({"success": False, "message": "Notification not found"}), 404

        # Return notification details
        response = {
            "success": True,
            "notification": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "button_text": getattr(notification, "button_text", None),
                "button_url": getattr(notification, "button_url", None),
                "segment": getattr(notification, "segment", None),
                "specific_users": getattr(notification, "specific_users", []),
                "schedule_date": notification.schedule_date.strftime(
                    "%d/%m/%Y %H:%M") if notification.schedule_date else None
            }
        }
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Fetch push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def generate_notification_uid(admin_uid):
    count = PushNotification.objects(admin_uid=admin_uid).count() + 1
    return f"NOTI_{str(count).zfill(2)}"