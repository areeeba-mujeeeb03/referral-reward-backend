from flask import request, jsonify

from main_app.models.admin.email_model import EmailTemplate
from main_app.models.admin.error_model import Errors
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.admin.links import ReferralReward
from main_app.models.user.reward import Reward
from main_app.models.admin.product_model import Product
import datetime
import logging
import random
from main_app.models.user.user import User

# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_reward_settings():
    try:
        data = request.get_json()

        # Validate input fields
        required_fields = ['referrer_reward', 'invitee_reward', 'conversion_rates']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        cr = data['conversion_rates']
        if not all(k in cr for k in ['meteor_to_star', 'star_to_meteor', 'reward_to_currency']):
            return jsonify({"error": "Invalid conversion rates format"}), 400

        # Upsert settings (only one document in this collection)
        ReferralReward.objects().update_one(
            set__referrer_reward=data['referrer_reward'],
            set__invitee_reward=data['invitee_reward'],
            set__conversion_rates=data['conversion_rates'],
            set__updated_at=datetime.datetime.now(),
            upsert=True
        )

        return jsonify({
            "message": "Reward settings updated successfully",
            "data": {
                "referrer_reward": data['referrer_reward'],
                "invitee_reward": data['invitee_reward'],
                "conversion_rates": data['conversion_rates']
            }
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

# def update_user_milestone(user_id, galaxy_name, meteors_earned):
#     reward = Reward.objects(user_id=user_id).first()
#     galaxy = Galaxy.objects(galaxy_name=galaxy_name).first()
#     if not reward or not galaxy:
#         return {"success": False, "message": "User or galaxy not found"}
#
#     reward.total_meteors += meteors_earned
#
#     progress = None
#     for galaxy in reward.galaxy_progress:
#         if galaxy["galaxy_name"] == galaxy_name:
#             progress = galaxy
#             break
#
#     if not progress:
#         progress = {
#             "galaxy_name": galaxy_name,
#             "earned_meteors": meteors_earned,
#             "milestones_completed": 0
#         }
#         reward.galaxy_progress.append(progress)
#     else:
#         progress["earned_meteors"] += meteors_earned
#
#     completed = progress["milestones_completed"]
#
#     if completed < len(galaxy.all_milestones):
#         milestone = galaxy.all_milestones[completed]
#         if progress["earned_meteors"] >= milestone.meteors_required_to_unlock:
#             reward.total_stars += milestone.milestone_reward
#             progress["milestones_completed"] += 1
#
#             reward.galaxy_name.append(galaxy_name)
#             reward.current_planet.append(milestone.milestone_name)
#
#             reward.reward_history.append({
#                 "milestone_id": milestone.milestone_id,
#                 "milestone_name": milestone.milestone_name,
#                 "galaxy": galaxy_name,
#                 "reward": milestone.milestone_reward
#             })
#
#             send_milestone_email(user_id, milestone.email_config)
#
#     reward.save()
#     return {"success": True, "message": "Milestone updated"}


def update_planet_and_galaxy(user_id):
    try:
        reward = Reward.objects(user_id=user_id).first()
        if not reward:
            return jsonify({"message": "Reward entry not found"}), 404

        all_galaxies = reward.galaxy_name
        if not all_galaxies:
            return jsonify({"message": "No galaxy assigned yet"}), 400

        current_galaxy_name = all_galaxies[-1]
        current_galaxy = Galaxy.objects(galaxy_name=current_galaxy_name).first()

        if not current_galaxy:
            return jsonify({"message": "This galaxy does not exist"}), 404

        total_meteors = reward.total_meteors
        milestone_unlocked = False

        for milestone in current_galaxy.all_milestones:
            if milestone.milestone_name not in reward.current_planet:
                if total_meteors >= milestone.meteors_required_to_unlock:
                    reward.update(push__current_planet=milestone.milestone_name)
                    milestone_unlocked = True
                    return jsonify({"message": f"New planet unlocked: {milestone.milestone_name}", "success": True}), 200

        if total_meteors >= current_galaxy.total_meteors_required:
            next_galaxy = Galaxy.objects(galaxy_name__nin=all_galaxies).first()
            if next_galaxy:
                reward.update(push__galaxy_name=next_galaxy.galaxy_name)
                return jsonify({"message": "New Galaxy Unlocked", "success": True}), 200
            else:
                return jsonify({"message": "No more galaxies available"}), 200

        if not milestone_unlocked:
            return jsonify({"message": "No new planet or galaxy unlocked yet"}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to update progress: {str(e)}"}), 500

def win_voucher(user_id):
    user = User.objects(user_id = user_id).first()
    try:
        if not user_id:
            logger.warning("Missing user_id in request body")
            return jsonify({'error': 'user_id is required'}), 400

        reward = Reward.objects(user_id=user_id).first()
        if not reward:
            logger.error(f"Reward profile not found for user_id: {user_id}")
            return jsonify({'error': 'Reward profile not found'}), 404

        products = Product.objects(
            status="Live",
            apply_offer=True,
            expiry_date__gte=datetime.datetime.now()
        )

        if not products:
            logger.info("No active products with offers available")
            return jsonify({'message': 'No offers available to win at this time'}), 400

        won_product = random.choice(products)

        if not won_product.voucher_code:
            logger.error(f"Product {won_product.uid} has no voucher_code generated.")
            return jsonify({'error': 'This offer is not properly configured'}), 500

        voucher_data = {
            "voucher_code": won_product.voucher_code,  # Shared voucher code
            "product_id": won_product.uid,
            "product_name": won_product.product_name,
            "discounted_amt": won_product.discounted_amt,
            "original_amt": won_product.original_amt,
            "off_percent": won_product.off_percent,
            "offer_type": won_product.offer_type,
            "expiry_date": won_product.expiry_date.isoformat(),
            "redeemed": False
        }

        if any(v['voucher_code'] == won_product.voucher_code for v in reward.all_vouchers):
            logger.info(f"User {user_id} already has voucher {won_product.voucher_code}")
            return jsonify({'message': 'You already won this voucher'}), 409

        reward.all_vouchers.append(voucher_data)
        reward.total_vouchers += 1
        reward.save()

        logger.info(f"User {user_id} won voucher {won_product.voucher_code}")
        return jsonify({
            "message": "Congratulations! You won a voucher.",
            "voucher": voucher_data
        }), 200

    except Exception as e:
        Errors(username=user.username, email=user.email, error_source="win voucher",
               error_type=f"Error in user redeeming voucher: {str(e)}").save()
        logger.exception(f"Error in user redeeming voucher: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
