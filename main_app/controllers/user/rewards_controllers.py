from flask import request, jsonify

from main_app.models.admin.admin_model import Admin
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
        if not all(k in cr for k in ['meteor_to_star', 'star_to_meteor', 'reward_to_currency']):
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

def update_planet_and_galaxy(user_id):
    try:
        reward = Reward.objects(user_id=user_id).first()

        all_galaxies = reward.galaxy_name

        current_galaxy_name = all_galaxies[-1]
        current_galaxy = Galaxy.objects(galaxy_name=current_galaxy_name).first()

        total_meteors = reward.current_meteors
        milestone_unlocked = False

        for milestone in current_galaxy.all_milestones:
            if milestone.milestone_name not in reward.current_planet:
                if total_meteors >= milestone.meteors_required_to_unlock:
                    reward.update(push__current_planet=milestone.milestone_name)
                    milestone_unlocked = True
                    return jsonify({"milestones": reward.current_planet, "galaxy": reward.galaxy_name,"meteors": reward.current_meteors,"success": True}), 200

        if total_meteors >= current_galaxy.total_meteors_required:
            next_galaxy = Galaxy.objects(galaxy_name__nin=all_galaxies).first()
            if next_galaxy:
                reward.update(push__galaxy_name=next_galaxy.galaxy_name)
                return jsonify({"milestones": reward.current_planet, "galaxy": reward.galaxy_name, "meteors": reward.current_meteors,"success": True}), 200

        if not milestone_unlocked:
            return jsonify({"milestones": reward.current_planet, "galaxy": reward.galaxy_name,"meteors": reward.current_meteors,}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to update progress: {str(e)}"}), 500

def win_voucher(user_id):
    if not user_id:
        logger.warning("Missing user_id in request body")
        return jsonify({'error': 'user_id is required'}), 400
    user = User.objects(user_id=user_id).only("user_id", "username", "email").first()

    try:
        if not user:
            logger.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        reward = Reward.objects(user_id=user_id).first()
        if not reward:
            logger.error(f"Reward profile not found for user_id: {user_id}")
            return jsonify({'error': 'Reward profile not found'}), 404

        # Get eligible products with live offers
        products = list(Product.objects(
            status="Live",
            apply_offer=True,
            expiry_date__gte=datetime.datetime.utcnow(),
            voucher_code__exists=True
        ))

        if not products:
            logger.info("No active products with offers available")
            return jsonify({'message': 'No offers available to win at this time'}), 400

        # Randomly select one product
        won_product = random.choice(products)

        if not won_product.voucher_code:
            logger.error(f"Product {won_product.uid} has no voucher_code generated.")
            return jsonify({'error': 'This offer is not properly configured'}), 500

        # Check if voucher already won
        if any(v['voucher_code'] == won_product.voucher_code for v in reward.all_vouchers):
            logger.info(f"User {user_id} already has voucher {won_product.voucher_code}")
            return jsonify({'message': 'You already won this voucher'}), 409

        now = datetime.datetime.utcnow()
        expiry = now + datetime.timedelta(days=7)

        voucher_data = {
            "voucher_code": won_product.voucher_code,
            "product_id": won_product.uid,
            "product_name": won_product.product_name,
            "discounted_amt": won_product.discounted_amt,
            "original_amt": won_product.original_amt,
            "off_percent": won_product.off_percent,
            "offer_type": won_product.offer_type,
            "start_date": now.isoformat(),
            "expiry_date": expiry.isoformat(),
            "status": "active",
            "redeemed": False
        }

        reward.all_vouchers.append(voucher_data)
        reward.total_vouchers += 1
        reward.unused_vouchers += 1
        reward.reward_history.append({
            "action": "voucher_won",
            "voucher_code": won_product.voucher_code,
            "timestamp": now
        })
        reward.save()

        logger.info(f"User {user_id} won voucher {won_product.voucher_code}")
        return jsonify({
            "message": "Congratulations! You won a voucher.",
            "voucher": voucher_data
        }), 200

    except Exception as e:
        logger.exception(f"Error in user redeeming voucher: {str(e)}")
        Errors(username=user.username if user else "unknown",
               email=user.email if user else "unknown",
               error_source="win voucher",
               error_type=f"Error in user redeeming voucher: {str(e)}").save()
        return jsonify({'error': 'Internal server error'}), 500

