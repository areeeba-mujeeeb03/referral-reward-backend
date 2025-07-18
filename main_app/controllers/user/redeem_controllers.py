from flask import request, jsonify

from main_app.models.admin.perks_model import ExclusivePerks
from main_app.models.user.reward import Reward
import datetime
import logging
import _strptime

from main_app.models.user.user import User

# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def redeem(card_type):
#     try:
#         print("start")
#         data = request.get_json()
#         user_id = data.get('user_id')
#         coupon_code = data.get('coupon_code')
#         print(data)
#
#         if card_type != "discount-coupon":
#             return jsonify({'error': 'Unsupported Type'}), 400
#
#         if not user_id or not coupon_code:
#             logger.warning("Missing required parameters in redeem request")
#             return jsonify({'error': 'user_id and coupon_code are required'}), 400
#
#         reward = Reward.objects(user_id=user_id).first()
#         if not reward:
#             logger.error(f"Reward not found for user_id: {user_id}")
#             return jsonify({'error': 'Reward profile not updated'}), 404
#
#         won_coupons = reward.discount_coupons
#         matched_coupon = None
#
#         for coupon in won_coupons:
#             if coupon.get('voucher_code') == coupon_code:
#                 matched_coupon = coupon
#                 break
#
#         if not matched_coupon:
#             return jsonify({"message": "Coupon not found", "success": False}), 404
#
#         expiry = matched_coupon.get('expiry_date')
#
#         if expiry and expiry < datetime.datetime.now():
#             return jsonify({"message": "This Coupon has expired", "success": False}), 400
#
#         won_coupons.remove(matched_coupon)
#
#         reward.update(
#             dec__unused_vouchers=1,
#             inc__used_vouchers=1,
#         )
#         reward.save()
#
#         return jsonify({
#             "congrats_text": "Congratulations! You have claimed your Discount Voucher",
#             "success": True
#         }), 200
#
#     except Exception as e:
#         logger.exception(f"Exception during voucher redemption: {str(e)}")
#         return jsonify({'error': 'Internal server error'}), 500


def redeem(card_type):
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if card_type == "discount-coupon":
            coupon_code = data.get('coupon_code')
            print(coupon_code)

            if not user_id or not coupon_code:
                logger.warning("Missing required parameters in redeem request")
                return jsonify({'error': 'user_id and coupon_code are required'}), 400

            reward = Reward.objects(user_id=user_id).first()
            if not reward:
                logger.error(f"Reward not found for user_id: {user_id}")
                return jsonify({'error': 'Reward profile not updated'}), 404

            won_coupons = reward.discount_coupons

            for coupon in won_coupons:
                if coupon.get('voucher_code') == coupon_code:
                    reward.update(
                        pull__discount_coupons={"voucher_code": coupon_code}
                    )
                    break

                expiry = coupon.get('expiry_date')

                if expiry < datetime.datetime.now():
                    return jsonify({"message": "This Coupon  has expired", "success": False}), 400

                reward.update(
                    dec__unused_vouchers=1,
                    inc__used_vouchers=1
                )
                reward.save()

                return jsonify({
                    "congrats_text": "Congratulations! You have claimed your Discount Voucher",
                    "success": True
                }), 200

        if card_type == "offers":
            off_percent = data.get("off_percent")
            product_id = data.get("product_id")

            if not user_id or not off_percent or not product_id:
                logger.warning("Missing required parameters in redeem request")
                return jsonify({'error': 'Missing required data.'}), 400



            # return jsonify({
            #     "congrats_text": "Congratulations! You have claimed your Discount Voucher",
            #     "success": True
            # }), 200
        #
        # if card_type == "discount-coupon":
        #     coupon_code = data.get('coupon_code')
        #     print(coupon_code)
        #
        #     if not user_id or not coupon_code:
        #         logger.warning("Missing required parameters in redeem request")
        #         return jsonify({'error': 'user_id and coupon_code are required'}), 400
        #
        #     reward = Reward.objects(user_id=user_id).first()
        #     if not reward:
        #         logger.error(f"Reward not found for user_id: {user_id}")
        #         return jsonify({'error': 'Reward profile not updated'}), 404
        #
        #     won_coupons = reward.discount_coupons
        #
        #     for coupon in won_coupons:
        #         if coupon.get('voucher_code') == coupon_code:
        #             reward.update(
        #                 pull__discount_coupons={"voucher_code": coupon_code}
        #             )
        #             break
        #
        #         expiry = coupon.get('expiry_date')
        #
        #         if expiry < datetime.datetime.now():
        #             return jsonify({"message": "This Coupon  has expired", "success": False}), 400
        #
        #         reward.update(
        #             dec__unused_vouchers=1,
        #             inc__used_vouchers=1
        #         )
        #         reward.save()
        #
        #         return jsonify({
        #             "congrats_text": "Congratulations! You have claimed your Discount Voucher",
        #             "success": True
        #         }), 200

        return jsonify({'error': 'Unsupported Type'}), 400

    except Exception as e:
        logger.exception(f"Exception during voucher redemption: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500