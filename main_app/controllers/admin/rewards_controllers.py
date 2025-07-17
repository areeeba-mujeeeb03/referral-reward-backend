import datetime
from flask import request, jsonify
from main_app.models.admin.links import ReferralReward
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.email_model import EmailTemplate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def set_reward_settings():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

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

        required_fields = ['referrer_reward', 'invitee_reward', 'conversion_rates']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        cr = data['conversion_rates']
        if not all(k in cr for k in ['meteors_to_stars', 'stars', 'stars_to_currency', "currency"]):
            return jsonify({"error": "Invalid conversion rates format"}), 400

        ReferralReward.objects(admin_uid = admin_uid).update_one(
            set__referrer_reward=data['referrer_reward'],
            set__invitee_reward=data['invitee_reward'],
            set__conversion_rates=data['conversion_rates'],
            set__updated_at=datetime.datetime.now(),
            upsert=True
        )

        return jsonify({
            "message": "Reward settings updated successfully",
            "success": True
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_milestone_email(email, email_template_type):
    try:
        template = EmailTemplate.objects(email_type= email_template_type).first()
        if not template:
            print(f"Email template  {email_template_type} not found.")
            return False

        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "areebamujeeb309@gmail.com"
        smtp_password = "rvph suey zpfl smpw"

        msg = MIMEMultipart('alternative')
        msg['From'] = f"{template.name} <{template.email}>"
        msg['To'] = email
        msg['Subject'] = template.subject
        msg.add_header('Reply-To', template.reply_to)
        content = template.content

        msg.attach(MIMEText(content, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(template.email, email, msg.as_string())
        server.quit()
        print(f"Email sent to {email} using template {email_template_type}")
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def create_galaxy():
    try:
        data = request.get_json()
        galaxy_name = data.get("galaxy_name")
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        total_milestones = data.get("total_milestones")
        highest_reward = data.get("highest_reward")
        stars = data.get("stars")

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

        if not galaxy_name or not admin_uid:
            return jsonify({"message": "Galaxy name and admin_uid are required"}), 400

        existing = Galaxy.objects(galaxy_name=galaxy_name, admin_uid=admin_uid).first()
        if existing:
            return jsonify({"message": "Galaxy already exists"}), 400

        galaxy = Galaxy(
            galaxy_name=galaxy_name,
            total_meteors_required=0,
            total_milestones=total_milestones,
            all_milestones=[],
            admin_uid=admin_uid,
            highest_reward = highest_reward,
            stars_to_be_achieved = stars
        )
        galaxy.save()
        return jsonify({"message": "Galaxy created successfully","success" : True}), 201

    except Exception as e:
        print(str(e))
        return jsonify({"message": "Galaxy creation failed"}), 500

def add_new_milestone():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        galaxy_name = data.get("galaxy_name")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
        milestone_description = data.get("milestone_description")

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

        if not all([milestone_name, milestone_reward, milestone_description, meteors_required_to_unlock]):
            return jsonify({"message": "All milestone fields are required"}), 400

        galaxy = Galaxy.objects(admin_uid=admin_uid, galaxy_name=galaxy_name).first()
        if not galaxy:
            return jsonify({"message": "Galaxy not found"}), 404

        for m in galaxy.all_milestones:
            if m.milestone_name == milestone_name:
                return jsonify({"message": "Milestone with this name already exists"}), 400

        milestone_id = f"GS_MID_{len(galaxy.all_milestones) + 1}"

        new_milestone = {
            "milestone_id": milestone_id,
            "milestone_name": milestone_name,
            "milestone_reward": milestone_reward,
            "meteors_required_to_unlock": meteors_required_to_unlock,
            "milestone_description": milestone_description
        }

        galaxy.update(push__all_milestones=new_milestone)
        galaxy.update(
            total_meteors_required=meteors_required_to_unlock,
            set__total_milestones=len(galaxy.all_milestones) + 1
        )

        return jsonify({"message": "Milestone added successfully"}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to add milestone: {str(e)}"}), 500


def update_milestone():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")
        galaxy_name = data.get("galaxy_name")
        milestone_id = data.get("milestone_id")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
        milestone_description = data.get("milestone_description")

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

        galaxy = Galaxy.objects(admin_uid=admin_uid, galaxy_name=galaxy_name).first()
        if not galaxy:
            return jsonify({"message": "Galaxy not found"}), 404

        updated = False
        for i, milestone in enumerate(galaxy.all_milestones):
            if milestone.milestone_id == milestone_id:
                galaxy.all_milestones[i] = {
                    "milestone_id": milestone_id,
                    "milestone_name": milestone_name,
                    "milestone_reward": milestone_reward,
                    "meteors_required_to_unlock": meteors_required_to_unlock,
                    "milestone_description": milestone_description
                }
                updated = True
                break
        if updated:
            galaxy.save()
            return jsonify({"message": "Milestone updated successfully"}), 200
        else:
            return jsonify({"message": "Milestone not found"}), 404

    except Exception as e:
        return jsonify({"message": f"Milestone update failed: {str(e)}"}), 500

def remove_milestone():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    galaxy_name = data.get("galaxy_name")
    milestone_name = data.get("milestone_name")

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

    exist_galaxy = Galaxy.objects(galaxy_name=galaxy_name).first()
    if not exist_galaxy:
        return jsonify({"message": "Galaxy with this name does not exist"})

    for milestone in exist_galaxy.all_milestones:
        if not milestone.get("milestone_name") == milestone_name:
            return jsonify({"message" : "milestone not found"})
        if milestone.get("milestone_name") == milestone_name:
           milestone_name.delete(admin_uid = admin_uid, milestone_name = milestone_name)
        return jsonify({"message": "Milestone with this name already exists"})