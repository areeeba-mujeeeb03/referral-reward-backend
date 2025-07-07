from flask import request, jsonify

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
    reward = Reward.objects(user_id = user_id).first()

    all_galaxies = reward.galaxy_name[-1]

    return all_galaxies


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