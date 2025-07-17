from flask import request, jsonify
from main_app.models.user.reward import Reward
import datetime
import logging
import _strptime

# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def redeem(card_type):
    try:
        print("start")
        data = request.get_json()
        user_id = data.get('user_id')
        print(data)
        # try:
        if card_type == "discount-coupon":
            coupon_code = data.get('coupon_code')
            print(coupon_code)
            if not user_id or not coupon_code:
                logger.warning("Missing required parameters in redeem request")
                return jsonify({'error': 'user_id and voucher_code are required'}), 400

            reward = Reward.objects(user_id=user_id).first()
            if not reward:
                logger.error(f"Reward not found for user_id: {user_id}")
                return jsonify({'error': 'Reward profile not updated'}), 404

            won_coupons = reward.discount_coupons

            for coupon in won_coupons:
                print(coupon)
                if coupon['voucher_code'] == coupon_code:
                    expiry = coupon['expiry_date']
                    print(expiry)
                    if expiry >= datetime.datetime.now():
                        return jsonify({"message": "This Coupon has expired",
                                        "success": True}), 200
                    # coupon.remove(
                    #     voucher_code = coupon_code
                    # )
                    reward.update(dec__unused_vouchers = 1,
                                  inc__used_vouchers = 1)
                    reward.save()
                    return jsonify({"congrats_text" : "Congratulations You have claimed your Discount Voucher",
                                    "success" : True}),200

                return "Not Done", 400

            return "Not Done", 400

        # except Exception as e:
        #     logger.exception(f"Exception during voucher redemption : {str(e)}")
        #     return jsonify({'error': 'Internal server error'}), 500

    except Exception as e:
        logger.exception(f"Exception during voucher redemption : {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500