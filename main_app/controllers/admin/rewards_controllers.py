import datetime
from flask import request, jsonify
from main_app.models.admin.links import ReferralReward
from main_app.models.admin.galaxy_model import Galaxy, GalaxyProgram, Milestone
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.email_model import EmailTemplate
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        if not all(required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        if type('referrer_reward') != int and type('invitee_reward') != int:
            return jsonify({"message" : "The type of referral and invitee reward must be an integer"})

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
        logger.error(f"Error sending email: {str(e)}")
        return False

def create_galaxy():
    try:
        data = request.get_json()
        galaxy_name = data.get("galaxy_name")
        program_id = data.get("program_id")
        admin_uid = data.get("admin_uid")
        total_milestones = data.get("total_milestones")
        highest_reward = data.get("highest_reward")
        stars = data.get("stars")

        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        galaxy_program = GalaxyProgram.objects(program_id=program_id).first()
        if not galaxy_program:
            galaxy_program = GalaxyProgram(program_id=program_id, admin_uid=admin_uid, galaxies=[])

        for galaxy in galaxy_program.galaxies:
            if galaxy.galaxy_name.lower() == galaxy_name.lower():
                return jsonify({"message": "Galaxy already exists in this program"}), 400

        galaxy_id = f"GXY_{len(galaxy_program.galaxies) + 1}"

        new_galaxy = Galaxy(
            galaxy_id=galaxy_id,
            galaxy_name=galaxy_name,
            total_meteors_required=0,
            highest_reward=highest_reward,
            total_milestones=total_milestones,
            stars_to_be_achieved=stars,
            milestones=[]
        )
        galaxy_program.galaxies.append(new_galaxy)
        galaxy_program.save()
        return jsonify({"message": "Galaxy created successfully", "success": True}), 201

    except Exception as e:
        return jsonify({"message": f"Galaxy creation failed: {str(e)}"}), 500


def add_new_milestone():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        program_id = data.get("program_id")
        galaxy_name = data.get("galaxy_name")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
        milestone_description = data.get("milestone_description")

        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        program = GalaxyProgram.objects(program_id=program_id, admin_uid=admin_uid).first()
        if not program:
            return jsonify({"message": "Program not found"}), 404

        for galaxy in program.galaxies:
            if galaxy.galaxy_name == galaxy_name:
                for m in galaxy.milestones:
                    if m.milestone_name == milestone_name:
                        return jsonify({"message": "Milestone already exists"}), 400

                milestone_id = f"MS_{len(galaxy.milestones) + 1}"
                new_milestone = Milestone(
                    milestone_id=milestone_id,
                    milestone_name=milestone_name,
                    milestone_reward=milestone_reward,
                    meteors_required_to_unlock=meteors_required_to_unlock,
                    milestone_description=milestone_description
                )
                galaxy.milestones.append(new_milestone)
                galaxy.total_milestones = len(galaxy.milestones)
                galaxy.total_meteors_required += meteors_required_to_unlock

                program.save()
                return jsonify({"message": "Milestone added successfully"}), 200

        return jsonify({"message": "Galaxy not found in this program"}), 404

    except Exception as e:
        return jsonify({"message": f"Failed to add milestone: {str(e)}"}), 500