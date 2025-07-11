import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from main_app.controllers.admin.how_it_work_controller import UPLOAD_FOLDER
from main_app.models.admin.galaxy_model import Galaxy, Milestone


def create_galaxy():
    try:
        data = request.get_json()
        galaxy_name = data.get("galaxy_name")
        admin_uid = data.get("admin_uid")

        if not galaxy_name or not admin_uid:
            return jsonify({"message": "Galaxy name and admin_uid are required"}), 400

        existing = Galaxy.objects(galaxy_name=galaxy_name, admin_uid=admin_uid).first()
        if existing:
            return jsonify({"message": "Galaxy already exists"}), 400

        galaxy = Galaxy(
            galaxy_name=galaxy_name,
            total_meteors_required=0,
            total_milestones=0,
            all_milestones=[],
            admin_uid=admin_uid
        )
        galaxy.save()
        return jsonify({"message": "Galaxy created successfully", "galaxy_id": str(galaxy.id)}), 201

    except Exception as e:
        return jsonify({"message": f"Galaxy creation failed: {str(e)}"}), 500

def add_new_milestone():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        galaxy_name = data.get("galaxy_name")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
        milestone_description = data.get("milestone_description")

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
        data = request.form.to_dict()
        admin_uid = data.get("admin_uid")
        galaxy_name = data.get("galaxy_name")
        milestone_id = data.get("milestone_id")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
        milestone_description = data.get("milestone_description")

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
    galaxy_name = data.get("galaxy_name")
    milestone_name = data.get("milestone_name")

    exist = Galaxy.objects(galaxy_name=galaxy_name).first()
    if not exist:
        return jsonify({"message": "Galaxy with this name does not exist"})

    for milestone in exist.all_milestones:
        if not milestone.get("milestone_name") == milestone_name:
            return jsonify({"message" : "milestone not found"})
        if milestone.get("milestone_name") == milestone_name:
           milestone_name.delete(admin_uid = admin_uid, milestone_name = milestone_name)
        return jsonify({"message": "Milestone with this name already exists"})
