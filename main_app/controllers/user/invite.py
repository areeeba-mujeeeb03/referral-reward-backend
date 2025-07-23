import datetime
import logging
from flask import request, jsonify, session
from main_app.models.user.user import User
from main_app.controllers.user.auth_controllers import validate_session_token
from main_app.models.admin.links import AppStats
from main_app.routes.admin.admin_routes import admin_bp

# ================

# Configuration and setup

# ===============

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from urllib.parse import quote_plus
def generate_msg(user, name):
    msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
            f"Join using my invite and enjoy exclusive offers on their products. \n\n"
            f"Use my invitation link : {user.invitation_link}\n"
           f" Or you can use my invitation code: {user.invitation_code}")
    encoded_msg = quote_plus(msg)

    return encoded_msg

def send_whatsapp_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"}), 404
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return jsonify({"success": False, "message": "Invalid access token"}), 401
        if user_exist.session_id != session_id:
            return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403
        if hasattr(user_exist, 'expiry_time') and user_exist.expiry_time:
            if datetime.datetime.now() > user_exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401
        if not user_exist.invitation_link:
            return jsonify({"success": False, "message": "Invitation link not found"}), 404

        msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
               f"Join using my invite and enjoy exclusive offers on their products. \n\n"
               f"Use my invitation link : {user_exist.invitation_link + "/wa" }\n"
               f" Or you can use my invitation code: {user_exist.invitation_code}")
        encoded_msg = quote_plus(msg)

        whatsapp_link = f"https://wa.me/?text={encoded_msg}"

        admin_uid = user_exist.admin_uid
        app_data = AppStats.objects(admin_uid=admin_uid).first()

        data = {"app_name": "WhatsApp", "total_sent": 1, "successful_registered": 0}

        if not app_data:
            app_data = AppStats(admin_uid=admin_uid, apps=[data])
            app_data.save()
        else:
            updated = False
            for app in app_data.apps:
                if app.get("app_name", "").lower() == "whatsapp":
                    app["total_sent"] += 1
                    updated = True
                    break
            if not updated:
                app_data.apps.append(data)
            app_data.save()

        return jsonify({
            "success": True,
            "link": whatsapp_link
        })

    except Exception as e:
        logger.error("WhatsApp invite error", exc_info=True)
        return jsonify({"success": False, "message": "Internal Server Error"}), 500



def send_twitter_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()


        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401
        
        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403
        
        if hasattr(user_exist, 'expiry_time') and user_exist.expiry_time:
            if datetime.datetime.now() > user_exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
               f"Join using my invite and enjoy exclusive offers on their products. \n\n"
               f"Use my invitation link : {user_exist.invitation_link + "/tw" }\n"
               f" Or you can use my invitation code: {user_exist.invitation_code}")
        encoded_msg = quote_plus(msg)
        twitter_link = f"https://twitter.com/intent/tweet?text={encoded_msg}"
        admin_uid = user_exist.admin_uid
        app_data = AppStats.objects(admin_uid=admin_uid).first()

        data = {"app_name": "Twitter", "total_sent": 1, "successful_registered": 0}

        if not app_data:
            app_data = AppStats(admin_uid=admin_uid, apps=[data])
            app_data.save()
        else:
            updated = False
            for app in app_data.apps:
                if app.get("app_name", "").lower() == "twitter":
                    app["total_sent"] += 1
                    updated = True
                    break
            if not updated:
                app_data.apps.append(data)
            app_data.save()

        return jsonify({
            "success": True,
            "link": twitter_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500


def send_telegram_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user_exist, 'expiry_time') and user_exist.expiry_time:
            if datetime.datetime.now() > user_exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
               f"Join using my invite and enjoy exclusive offers on their products. \n\n"
               f"Use my invitation link : {user_exist.invitation_link + "/tele" }\n"
               f" Or you can use my invitation code: {user_exist.invitation_code}")
        encoded_msg = quote_plus(msg)
        telegram_link = f"https://t.me/share/url?url={quote_plus(user_exist.invitation_link)}&text={encoded_msg}"
        admin_uid = user_exist.admin_uid
        app_data = AppStats.objects(admin_uid=admin_uid).first()

        data = {"app_name": "Telegram", "total_sent": 1, "successful_registered": 0}

        if not app_data:
            app_data = AppStats(admin_uid=admin_uid, apps=[data])
            app_data.save()
        else:
            updated = False
            for app in app_data.apps:
                if app.get("app_name", "").lower() == "telegram":
                    app["total_sent"] += 1
                    updated = True
                    break
            if not updated:
                app_data.apps.append(data)
            app_data.save()

        return jsonify({
            "success": True,
            "link": telegram_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500

def send_facebook_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user_exist, 'expiry_time') and user_exist.expiry_time:
            if datetime.datetime.now() > user_exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
               f"Join using my invite and enjoy exclusive offers on their products. \n\n"
               f"Use my invitation link : {user_exist.invitation_link + "/fb" }\n"
               f" Or you can use my invitation code: {user_exist.invitation_code}")
        encoded_msg = quote_plus(msg)

        facebook_link = f"https://www.facebook.com/sharer/sharer.php?u={quote_plus(user_exist.invitation_link)}"
        admin_uid = user_exist.admin_uid
        app_data = AppStats.objects(admin_uid=admin_uid).first()

        data = {"app_name": "FaceBook", "total_sent": 1, "successful_registered": 0}

        if not app_data:
            app_data = AppStats(admin_uid=admin_uid, apps=[data])
            app_data.save()
        else:
            updated = False
            for app in app_data.apps:
                if app.get("app_name", "").lower() == "facebook":
                    app["total_sent"] += 1
                    updated = True
                    break
            if not updated:
                app_data.apps.append(data)
            app_data.save()

        return jsonify({
            "success": True,
            "link": facebook_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500

def send_linkedin_invite():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        user_exist = User.objects(user_id=user_id).first()

        if not user_exist:
            return jsonify({"success": False, "message": "User does not exist"})
        if not access_token or not session_id:
            return jsonify({"message": "Missing token or session", "success": False}), 400
        if user_exist.access_token != access_token:
            return ({"success": False,
                     "message": "Invalid access token"}), 401

        if user_exist.session_id != session_id:
            return ({"success": False,
                     "message": "Session mismatch or invalid session"}), 403

        if hasattr(user_exist, 'expiry_time') and user_exist.expiry_time:
            if datetime.datetime.now() > user_exist.expiry_time:
                return ({"success": False,
                         "message": "Access token has expired"}), 401

        if not user_exist or not user_exist.invitation_link:
            return jsonify({"success": False, "message": "User or invitation link not found"}), 404

        msg = (f"Hey! I’m using Wealth Elite and thought you’d love it too! "
               f"Join using my invite and enjoy exclusive offers on their products. \n\n"
               f"Use my invitation link : {user_exist.invitation_link + "/ln" }\n"
               f" Or you can use my invitation code: {user_exist.invitation_code}")
        encoded_msg = quote_plus(msg)

        linkedin_link = f"https://www.linkedin.com/sharer/sharer.php?u={quote_plus(user_exist.invitation_link)}"
        admin_uid = user_exist.admin_uid
        app_data = AppStats.objects(admin_uid=admin_uid).first()

        data = {"app_name": "LinkedIn", "total_sent": 1, "successful_registered": 0}

        if not app_data:
            app_data = AppStats(admin_uid=admin_uid, apps=[data])
            app_data.save()
        else:
            updated = False
            for app in app_data.apps:
                if app.get("app_name", "").lower() == "facebook":
                    app["total_sent"] += 1
                    updated = True
                    break
            if not updated:
                app_data.apps.append(data)
            app_data.save()

        return jsonify({
            "success": True,
            "link": linkedin_link
        })

    except Exception as e:
        logger.error(f"Twitter invite error: {str(e)}")
        return jsonify({"success": False, "message": "Internal Server Error"}), 500