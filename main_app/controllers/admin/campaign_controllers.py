from flask import Flask, request, jsonify
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.campaign_model import Campaign
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.admin.links import AppStats, ReferralReward
from main_app.models.admin.participants_model import Participants

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_program_id(admin_uid):
    prog_doc = Admin.objects(admin_uid=admin_uid).first()
    count = 1
    if prog_doc:
        for program in prog_doc.all_campaigns:
            if program:
                  count = len(prog_doc.all_campaigns) + 1
    else:
        count = 1
    return f"PROG_{str(count).zfill(2)}"

def create_new_campaign():
    try:
        logger.info("Initializing New Campaign")
        data = request.get_json()

        admin_uid = data.get("admin_uid")
        program_name = data.get("program_name")
        base_url = data.get("url")

        find = Campaign.objects(admin_uid = admin_uid)
        find_admin = Admin.objects(admin_uid=admin_uid).first()
        if not find_admin:
            return jsonify({"message": "User Not Found", "success": False}), 400

        if find == program_name:
            return jsonify({"message": "Campaign with this name already exists", "success": False}), 400

        camp = Campaign(
            admin_uid = admin_uid,
            program_name = program_name,
            base_url = base_url
        ).save()

        for campaign in find_admin.all_campaigns:
            if campaign['program_name'].strip().lower() == program_name.strip().lower():
                return jsonify({"message": "Campaign with this name already exists", "success": False}), 400

        new_campaign = {
            "program_name": program_name,
            "program_id": camp.program_id,
            "base_url": base_url
        }

        find_admin.all_campaigns.append(new_campaign)
        find_admin.save()
        initialize_admin_data(admin_uid, camp.program_id)
        return jsonify({"message": "Successfully Created a Campaign", "success": True}), 201

    except Exception as e:
        logger.error(f"Failed to initialize campaign as {str(e)}")
        return jsonify({"message": "Failed to add Campaign", "success": False}), 400

def initialize_admin_data(admin_uid, program_id):
    Participants(
        admin_uid = admin_uid,
        program_id = program_id
    ).save()
    AppStats(
        admin_uid=admin_uid,
        program_id = program_id
    ).save()
    ReferralReward(
        admin_uid=admin_uid,
        program_id = program_id
    ).save()
    Galaxy(
        admin_uid=admin_uid,
        program_id = program_id
    ).save()
    return "done", 200
