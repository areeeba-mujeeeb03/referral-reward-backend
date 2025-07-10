import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from main_app.controllers.admin.how_it_work_controller import UPLOAD_FOLDER
from main_app.models.admin.galaxy_model import Galaxy, Milestone


def rewards():
    try:
        data = request.get_json()
        referrer_reward = data.get("referrer_reward")
        referee_reward = data.get("referee_reward")
        image = request.files.get("image")

    except Exception as e:
        return

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
        data = request.form.to_dict()
        admin_uid = data.get("admin_uid")
        galaxy_name = data.get("galaxy_name")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = int(data.get("meteors_required_to_unlock", 0))
        milestone_description = data.get("milestone_description")

        image = request.files.get("image")

        if not all([milestone_name, milestone_reward, milestone_description, meteors_required_to_unlock]):
            return jsonify({"message": "All milestone fields are required"}), 400

        # Save image if provided
        image_url = None
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = f"/{image_path}"

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
            "milestone_description": milestone_description,
            "image": image_url
        }

        galaxy.update(push__all_milestones=new_milestone)
        galaxy.update(
            inc__total_meteors_required=meteors_required_to_unlock,
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
        image = request.files.get("image")

        galaxy = Galaxy.objects(admin_uid=admin_uid, galaxy_name=galaxy_name).first()
        if not galaxy:
            return jsonify({"message": "Galaxy not found"}), 404

        updated = False
        for i, milestone in enumerate(galaxy.all_milestones):
            if milestone.milestone_id == milestone_id:
                if image:
                    filename = secure_filename(image.filename)
                    image_path = os.path.join(UPLOAD_FOLDER, filename)
                    image.save(image_path)
                    image_url = f"/{image_path}"
                else:
                    image_url = milestone.image

                galaxy.all_milestones[i] = {
                    "milestone_id": milestone_id,
                    "milestone_name": milestone_name,
                    "milestone_reward": milestone_reward,
                    "meteors_required_to_unlock": meteors_required_to_unlock,
                    "milestone_description": milestone_description,
                    "image": image_url
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

# def add_new_milestones():
#     try:
#         data = request.get_json()
#         admin_uid = data.get("admin_uid")
#         galaxy_name = data.get("galaxy_name")
#         milestone_name = data.get("milestone_name")
#         milestone_reward = data.get("milestone_reward")
#         meteors_required_to_unlock = data.get("meteors_to_unlock")
#         image = request.files.get("image")
#         milestone_description = data.get("milestone_description")
#
#         if not milestone_description or not milestone_reward or not milestone_name:
#             return jsonify({"message" : "All Fields are required"})
#
#         if image in data:
#             filename = secure_filename(image.filename)
#             image_path = os.path.join(UPLOAD_FOLDER, filename)
#             image.save(image_path)
#             image_url = f"/{image_path}"
#
#         exist = Galaxy.objects(admin_uid = admin_uid, galaxy_name = galaxy_name).first()
#         if not exist:
#             return jsonify({"message" : "Galaxy with this name doesnot exist"})
#         for milestone in exist.all_milestones:
#             if milestone.get("milestone_name") == milestone_name:
#                 return jsonify({"message": "Milestone with this name already exists"})
#         if exist:
#             milestone_id = f"GS_MID_{len(exist.all_milestones) + 1}"
#             exist.update(push__all_milestones ={ "milestone_id" : milestone_id,
#                                                  "milestone_name": milestone_name,
#                                                  "milestone_reward" : milestone_reward,
#                                                  "meteors_required_to_unlock" : meteors_required_to_unlock,
#                                                  "milestone_description" : milestone_description,
#                                                  "image" : image})
#             exist.update(
#                 total_meteors_required = meteors_required_to_unlock
#             )
#
#             return jsonify({"message" : "Milestone added successfully"}),200
#     except Exception as e:
#         return jsonify({"message" : f"Adding new milestone failed : {str(e)}"})

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
