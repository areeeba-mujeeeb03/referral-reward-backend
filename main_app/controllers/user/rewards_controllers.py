from flask import jsonify

from main_app.models.admin.discount_coupon_model import ProductDiscounts
from main_app.models.admin.error_model import Errors
from main_app.models.admin.galaxy_model import Galaxy
from main_app.models.user.reward import Reward
from main_app.models.admin.product_model import Product
import datetime
import logging
import random
from main_app.models.user.user import User

# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            return jsonify({"milestones": reward.current_planet,
                            "galaxy": reward.galaxy_name,"meteors": reward.current_meteors, "total_meteors" : reward.total_meteors_earned}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to update progress: {str(e)}"}), 500

def win_voucher(user_id):
    if not user_id:
        logger.warning("Missing user_id in request body")
        return jsonify({'error': 'user_id is required'}), 400

    user = User.objects(user_id=user_id).first()

    try:
        if not user:
            logger.warning(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        reward = Reward.objects(user_id=user_id).first()
        if not reward:
            logger.error(f"Reward profile not found for user_id: {user_id}")
            return jsonify({'error': 'Reward profile not found'}), 404

        products = ProductDiscounts.objects(admin_uid = user.admin_uid).first()

        valid_coupons = []

        for coupon in products.coupons:
            if coupon['end_date'] and coupon['end_date'] >= datetime.datetime.now():
                valid_coupons.append(coupon)
        won_product = random.choice(valid_coupons)

        if not won_product['coupon_code']:
            logger.error(f"Product {won_product.product_name} has no voucher_code generated.")
            return jsonify({'error': 'This offer is not properly configured'}), 500

        for v in reward.discount_coupons:
            if v['voucher_code'] == won_product['coupon_code']:
                already_has_voucher = True
                if already_has_voucher :
                    return jsonify({"message" : "Already won voucher"})

        now = datetime.datetime.now()
        expiry = now + datetime.timedelta(days=7)
        print(won_product)

        voucher_data = {
            "voucher_code": won_product['coupon_code'],
            "product_id": won_product['product_id'],
            "discounted_amt": won_product['discount_amt'],
            "original_amt": won_product['original_amt'],
            "off_percent": won_product['off_percent'],
            "offer_desc" : won_product['description'],
            "status": "active",
            "redeemed": False
        }

        reward.discount_coupons.append(voucher_data)
        reward.total_vouchers += 1
        reward.unused_vouchers += 1
        # reward.reward_history.append({
        #     "action": "voucher_won",
        #     "voucher_code": won_product.coupon_code,
        #     "expiry": now
        # })
        reward.save()

        logger.info(f"User {user.username} won voucher {won_product['coupon_code']}")
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