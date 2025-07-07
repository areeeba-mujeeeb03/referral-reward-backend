import os
from flask import request, jsonify
from werkzeug.utils import secure_filename
from main_app.controllers.admin.how_it_work_controller import UPLOAD_FOLDER
from main_app.models.admin.galaxy_model import Galaxy

def rewards():
    try:
        data = request.get_json()
        referrer_reward = data.get("referrer_reward")
        referee_reward = data.get("referee_reward")
        image = request.files.get("image")

    except Exception as e:
        return


def add_new_galaxy():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        galaxy_name = data.get("galaxy_name")
        total_milestones = data.get("no_of_milestones")

        exist = Galaxy.objects(admin_uid = admin_uid, galaxy_name = galaxy_name).first()
        if exist:
            return jsonify({"message" : "Galaxy with this name already exists"}),400
        else:
            save = Galaxy(galaxy_name = galaxy_name, total_milestones = total_milestones)
            save.save()
            return jsonify({"message" : "New Galaxy Added"})

    except Exception as e:
        return jsonify({"message" : f"Adding new Planet Failed! {str(e)}"}), 400

def add_new_milestones():
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        galaxy_name = data.get("galaxy_name")
        milestone_name = data.get("milestone_name")
        milestone_reward = data.get("milestone_reward")
        meteors_required_to_unlock = data.get("meteors_to_unlock")
        image = request.files.get("image")
        milestone_description = data.get("milestone_description")

        if not milestone_description or not milestone_reward or not milestone_name:
            return jsonify({"message" : "All Fields are required"})

        if image in data:
            filename = secure_filename(image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = f"/{image_path}"

        exist = Galaxy.objects(admin_uid = admin_uid, galaxy_name = galaxy_name).first()
        if not exist:
            return jsonify({"message" : "Galaxy with this name doesnot exist"})
        for milestone in exist.all_milestones:
            if milestone.get("milestone_name") == milestone_name:
                return jsonify({"message": "Milestone with this name already exists"})
        if exist:
            milestone_id = f"GS_MID_{len(exist.all_milestones) + 1}"
            exist.update(push__all_milestones ={ "milestone_id" : milestone_id,
                                                 "milestone_name": milestone_name,
                                                 "milestone_reward" : milestone_reward,
                                                 "meteors_required_to_unlock" : meteors_required_to_unlock,
                                                 "milestone_description" : milestone_description,
                                                 "image" : image})
            exist.update(
                total_meteors_required = meteors_required_to_unlock
            )

            return jsonify({"message" : "Milestone added successfully"}),200
    except Exception as e:
        return jsonify({"message" : f"Adding new milestone failed : {str(e)}"})

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
