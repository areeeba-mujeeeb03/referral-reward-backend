import datetime
from flask import request, jsonify

from main_app.models.admin.campaign_model import Campaign
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

        galaxies_data = data.get("galaxies", [])
        program_id = data.get("program_id")
        admin_uid = data.get("admin_uid")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404
        # if admin.access_token != access_token:
        #     return jsonify({"success": False, "message": "Invalid access token"}), 401
        # if admin.session_id != session_id:
        #     return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403
        # if hasattr(admin, 'expiry_time') and admin.expiry_time:
        #     if datetime.datetime.now() > admin.expiry_time:
        #         return jsonify({"success": False, "message": "Access token has expired"}), 401

        if not all([program_id, admin_uid]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        existing_program = Campaign.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not existing_program:
            return jsonify({"success": False, "message": "No such Campaign exists"}), 404

        galaxy_program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not galaxy_program:
            galaxy_program = GalaxyProgram(program_id=program_id, admin_uid=admin_uid, galaxies=[])

        existing_galaxy_names = {g.galaxy_name.lower() for g in galaxy_program.galaxies}

        created_galaxies = []
        for galaxy_data in galaxies_data:
            galaxy_name = galaxy_data.get("galaxy_name")
            total_milestones = galaxy_data.get("total_milestones")
            highest_reward = galaxy_data.get("highest_reward")
            stars = galaxy_data.get("stars")
            milestones_data = galaxy_data.get("milestones", [])

            if not galaxy_name:
                continue

            if galaxy_name.lower() in existing_galaxy_names:
                continue

            galaxy_id = f"GXY_{len(galaxy_program.galaxies) + 1}"

            milestone_objects = []
            for m in milestones_data:
                milestone = Milestone(
                    milestone_id=m.get("milestone_id"),
                    milestone_name=m.get("milestone_name"),
                    meteors_required_to_unlock=m.get("meteors_required_to_unlock", 0),
                    milestone_reward=m.get("milestone_reward", 0),
                    milestone_description=m.get("milestone_description", "")
                )
                milestone_objects.append(milestone)

            new_galaxy = Galaxy(
                galaxy_id=galaxy_id,
                galaxy_name=galaxy_name,
                total_meteors_required=0,
                highest_reward=highest_reward,
                total_milestones=total_milestones,
                stars_to_be_achieved=stars,
                milestones=milestone_objects
            )

            galaxy_program.galaxies.append(new_galaxy)
            created_galaxies.append(new_galaxy)
            existing_galaxy_names.add(galaxy_name.lower())

        galaxy_program.save()

        return jsonify({
            "success": True,
            "message": f"{len(created_galaxies)} galaxies created successfully",
            "created_galaxies": [g.to_mongo().to_dict() for g in created_galaxies]
        }), 201

    except Exception as e:
        logger.error(f"{str(e)}")
        return jsonify({"success": False, "message": f"Galaxy creation failed: {str(e)}"}), 500


def get_galaxy_details():
    try:
        data = request.get_json()

        program_id = data.get("program_id")
        admin_uid = data.get("admin_uid")
        galaxy_id = data.get("galaxy_id")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        if not all([program_id, admin_uid, galaxy_id, access_token, session_id]):
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404
        if admin.access_token != access_token:
            return jsonify({"success": False, "message": "Invalid access token"}), 401
        if admin.session_id != session_id:
            return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403
        if hasattr(admin, 'expiry_time') and admin.expiry_time:
            if datetime.datetime.now() > admin.expiry_time:
                return jsonify({"success": False, "message": "Access token has expired"}), 401

        program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not program:
            return jsonify({"success": False, "message": "No such GalaxyProgram found"}), 404

        galaxy_data = None
        for galaxy in program.galaxies:
            if galaxy.galaxy_id == galaxy_id:
                galaxy_data = galaxy
                break

        if not galaxy_data:
            return jsonify({"success": False, "message": "Galaxy not found"}), 404

        milestones_list = []
        for m in galaxy_data.milestones:
            milestones_list.append({
                "milestone_id": m.milestone_id,
                "milestone_name": m.milestone_name,
                "meteors_required_to_unlock": m.meteors_required_to_unlock,
                "milestone_reward": m.milestone_reward,
                "milestone_description": m.milestone_description
            })

        response = {
            "success": True,
            "galaxy": {
                "galaxy_id": galaxy_data.galaxy_id,
                "galaxy_name": galaxy_data.galaxy_name,
                "total_milestones": galaxy_data.total_milestones,
                "highest_reward": galaxy_data.highest_reward,
                "stars": galaxy_data.stars_to_be_achieved,
                "milestones": milestones_list
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "message": f"Failed to get galaxy data: {str(e)}"}), 500


# def create_galaxy():
#     try:
#         data = request.get_json()
#         galaxy_name = data.get("galaxy_name")
#         program_id = data.get("program_id")
#         admin_uid = data.get("admin_uid")
#         total_milestones = data.get("total_milestones")
#         highest_reward = data.get("highest_reward")
#         stars = data.get("stars")
#         milestones = data.get("milestones" ,[])
#         access_token = data.get("mode")
#         session_id = data.get("log_alt")
#
#         admin = Admin.objects(admin_uid=admin_uid).first()
#
#         if not admin:
#             return jsonify({"success": False, "message": "User does not exist"}), 404
#
#         if not admin_uid or not access_token or not session_id:
#             return jsonify({"message": "Missing required fields", "success": False}), 400
#
#         if admin.access_token != access_token:
#             return ({"success": False,
#                      "message": "Invalid access token"}), 401
#
#         if admin.session_id != session_id:
#             return ({"success": False,
#                      "message": "Session mismatch or invalid session"}), 403
#
#         if hasattr(admin, 'expiry_time') and admin.expiry_time:
#             if datetime.datetime.now() > admin.expiry_time:
#                 return jsonify({"success": False, "message": "Access token has expired"}), 401
#
#         existing_program = Campaign.objects(admin_uid = admin_uid, program_id = program_id).first()
#         if not existing_program:
#             return jsonify({"message" : "No such Campaign exists"}), 404
#
#         galaxy_program = GalaxyProgram.objects(admin_uid = admin_uid, program_id=program_id).first()
#         if not galaxy_program:
#             galaxy_program = GalaxyProgram(program_id=program_id, admin_uid=admin_uid, galaxies=[])
#
#         for galaxy in galaxy_program.galaxies:
#             if galaxy['galaxy_name'].lower() == galaxy_name.lower():
#                 return jsonify({"message": "This galaxy name already exists in this program"}), 400
#
#         galaxy_id = f"GXY_{len(galaxy_program.galaxies) + 1}"
#
#         new_galaxy = Galaxy(
#             galaxy_id=galaxy_id,
#             galaxy_name=galaxy_name,
#             total_meteors_required=0,
#             highest_reward=highest_reward,
#             total_milestones=total_milestones,
#             stars_to_be_achieved=stars,
#             milestones=[]
#         )
#         galaxy_program.galaxies.append(new_galaxy)
#         galaxy_program.save()
#         new_galaxy.milestones.append(milestones)
#         return jsonify({"message": "Galaxy created successfully", "success": True}), 201
#
#     except Exception as e:
#         return jsonify({"message": f"Galaxy creation failed: {str(e)}"}), 500
#
#
# def add_new_milestone():
#     try:
#         data = request.get_json()
#         admin_uid = data.get("admin_uid")
#         program_id = data.get("program_id")
#         galaxy_name = data.get("galaxy_name")
#         milestones = data.get("milestones", [])
#         # milestone_name = data.get("milestone_name")
#         # milestone_reward = data.get("milestone_reward")
#         # meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
#         # milestone_description = data.get("milestone_description")
#         access_token = data.get("mode")
#         session_id = data.get("log_alt")
#
#         admin = Admin.objects(admin_uid=admin_uid).first()
#
#         if not admin:
#             return jsonify({"success": False, "message": "User does not exist"}), 404
#
#         if not admin_uid or not access_token or not session_id:
#             return jsonify({"message": "Missing required fields", "success": False}), 400
#
#         if admin.access_token != access_token:
#             return ({"success": False,
#                      "message": "Invalid access token"}), 401
#
#         if admin.session_id != session_id:
#             return ({"success": False,
#                      "message": "Session mismatch or invalid session"}), 403
#
#         if hasattr(admin, 'expiry_time') and admin.expiry_time:
#             if datetime.datetime.now() > admin.expiry_time:
#                 return jsonify({"success": False, "message": "Access token has expired"}), 401
#
#         existing_program = Campaign.objects(admin_uid=admin_uid, program_id=program_id).first()
#         if not existing_program:
#             return jsonify({"message": "No such Campaign exists"}), 404
#
#         program = GalaxyProgram.objects(program_id=program_id, admin_uid=admin_uid).first()
#         if not program:
#             return jsonify({"message": "Program not found", "success" : True}), 404
#
#         for m in milestones:
#             if not m['milestone_name'] and not m['milestone_description'] and not m['milestone_reward'] and not m['meteors_required_to_unlock']:
#                 return jsonify({"message" : "Missing required fields", "success" : False}), 400
#
#         for m in milestones:
#             for galaxy in program.galaxies:
#                 if galaxy.galaxy_name == galaxy_name:
#                     for m in galaxy.milestones:
#                         if m.milestone_name == m['milestone_name']:
#                             return jsonify({"message": "Milestone already exists"}), 400
#
#                 milestone_id = f"MS_{len(galaxy.milestones) + 1}"
#                 new_milestone = Milestone(
#                     milestone_id=milestone_id,
#                     milestone_name=m['milestone_name'],
#                     milestone_reward=m['milestone_reward'],
#                     meteors_required_to_unlock=m['meteors_required_to_unlock'],
#                     milestone_description=m['milestone_description']
#                 )
#                 program.galaxies.milestones.append(milestones)
#                 galaxy.total_milestones = len(galaxy.milestones)
#                 galaxy.total_meteors_required += m['meteors_required_to_unlock']
#
#                 program.save()
#
#                 return jsonify({"message": "Milestone added successfully"}), 200
#
#         return jsonify({"message": "Galaxy not found in this program"}), 404
#
#     except Exception as e:
#         return jsonify({"message": f"Failed to add milestone: {str(e)}"}), 500