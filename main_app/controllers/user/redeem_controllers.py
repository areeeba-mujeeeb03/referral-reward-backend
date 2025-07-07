from flask import request, jsonify
from main_app.models.user.reward import Reward
import datetime
import logging


# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def redeem_voucher():
    try:
        user_id = request.json.get('user_id')
        voucher_code = request.json.get('voucher_code')

        if not user_id or not voucher_code:
            logger.warning("Missing required parameters in redeem request")
            return jsonify({'error': 'user_id and voucher_code are required'}), 400

        reward = Reward.objects(user_id=user_id).first()
        if not reward:
            logger.error(f"Reward not found for user_id: {user_id}")
            return jsonify({'error': 'Reward profile not found'}), 404

        for voucher in reward.all_vouchers:
            if voucher['voucher_code'] == voucher_code:
                if voucher['redeemed']:
                    logger.info(f"Voucher {voucher_code} already redeemed")
                    return jsonify({'message': 'Voucher already redeemed'}), 400

                expiry = datetime.datetime.fromisoformat(voucher['expiry_date'])
                if expiry < datetime.datetime.now():
                    logger.info(f"Voucher {voucher_code} expired")
                    return jsonify({'message': 'Voucher expired'}), 400

                voucher['redeemed'] = True
                reward.redeemed_meteors += 50  # Adjust based on logic
                reward.reward_history.append({
                    "voucher_code": voucher_code,
                    "redeemed_at": datetime.datetime.now().isoformat(),
                    "product_id": voucher['product_id'],
                    "discount_applied": voucher['off_percent']
                })
                reward.save()

                logger.info(f"Voucher {voucher_code} redeemed by user {user_id}")
                return jsonify({'message': 'Voucher redeemed successfully'}), 200

        logger.warning(f"Voucher {voucher_code} not found for user {user_id}")
        return jsonify({'error': 'Voucher not found'}), 404

    except Exception as e:
        logger.exception(f"Exception during voucher redemption : {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500