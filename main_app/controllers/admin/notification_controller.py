from flask import request, jsonify
import os, datetime, logging
from main_app.models.admin.notification_model import  PushNotification


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------Add Puch Notification

def create_push_notification():
    try:
        logger.info(f"Add push notification API called:")        
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        title = data.get("title")
        message = data.get("message")
        button_text = data.get("button_text")
        button_url = data.get("button_url")
        segment = data.get("segment", "All")
        specific_users = data.get("specific_users", [])
        date_str = data.get("date")  # Format: DD/MM/YYYY or DD-MM-YYYY
        time_str = data.get("time")  # Format: HH:MM (24h)

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

        notification = PushNotification(
            admin_uid=admin_uid,
            title=title,
            message=message,
            button_text=button_text,
            button_url=button_url,
            segment=segment,
            specific_users=specific_users,
            schedule_date=schedule_date
        )
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
        admin_uid = request.args.get("admin_uid")
        if not admin_uid:
            return jsonify({"error": "Missing admin_uid"}), 400

        notifications = PushNotification.objects(admin_uid=admin_uid).order_by('-created_at')
        result = []

        for n in notifications:
            result.append({
                "title": n.title,
                "message": n.message,
                "button_text": n.button_text,
                "button_url": n.button_url,
                "segment": n.segment,
                "specific_users": n.specific_users,
                "schedule_date": n.schedule_date.strftime("%d/%m/%Y %H:%M") if n.schedule_date else "",
                "created_at": n.created_at.strftime("%d/%m/%Y %H:%M")
            })

        return jsonify({"success": True, "notifications": result}), 200

    except Exception as e:
        logger.error(f"list push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


# ---------------------------------------------------------------------------

#------- Update notification

def update_push_notification(notification_id):
    try:
        data = request.get_json()
        notification = PushNotification.objects(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 404

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
        notification = PushNotification.objects(id=notification_id).first()
        if not notification:
            return jsonify({"error": "Notification not found"}), 400

        notification.delete()
        logger.info(f"Delete push notification")
        return jsonify({"success": True, "message": "Notification deleted"}), 200

    except Exception as e:
        logger.error(f"Delete push notification failed: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

