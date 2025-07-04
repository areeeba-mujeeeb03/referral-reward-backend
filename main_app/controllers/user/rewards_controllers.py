from flask import request, jsonify
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.user.reward import Reward


def update_planet_and_galaxy(user_id):
    reward = Reward.objects(user_id = user_id).first()

    all_galaxies = reward.galaxy_name[-1]

    return all_galaxies

print(update_planet_and_galaxy('WE_UID_2'))