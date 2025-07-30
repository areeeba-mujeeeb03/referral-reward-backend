from flask import request, jsonify

from main_app.models.admin.perks_model import ExclusivePerks
from main_app.models.admin.prize_model import PrizeDetail, AdminPrizes
from main_app.models.admin.product_model import Product
from main_app.models.admin.product_offer_model import Offer
from main_app.models.user.reward import Reward
import datetime
import logging
from main_app.models.user.user import User

# Configure logging for OTP operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def redeem(card_type):
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        user = User.objects(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if card_type == "discount-coupon":
            return redeem_discount_coupon(data, user)

        elif card_type == "offers":
            return redeem_offer(data, user)

        elif card_type == "exciting-prizes":
            return redeem_exciting_prize(data, user)

        else:
            return jsonify({'error': 'Invalid card_type'}), 400

    except Exception as e:
        logger.exception(f"Exception during voucher redemption: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500



def redeem_discount_coupon(data, user):
    try:
        user_id = user.user_id
        coupon_code = data.get('coupon_code')

        if not coupon_code:
            logger.warning("Missing coupon_code in redeem request")
            return jsonify({'error': 'coupon_code is required'}), 400

        reward = Reward.objects(user_id=user_id).first()
        if not reward:
            logger.error(f"Reward not found for user_id: {user_id}")
            return jsonify({'error': 'Reward profile not updated'}), 404

        for coupon in reward.discount_coupons:
            if coupon.get('coupon_code') == coupon_code:
                expiry = coupon.get('expiry_date')
                if expiry and expiry < datetime.datetime.now():
                    return jsonify({"message": "This coupon has expired", "success": False}), 400

                coupon['redeemed'] = True
                reward.update(
                    pull__discount_coupons={"coupon_code": coupon_code},
                    dec__unused_vouchers=1,
                    inc__used_vouchers=1
                )
                reward.save()

                return jsonify({
                    "congrats_text": "Congratulations! You have claimed your Discount Voucher",
                    "success": True
                }), 200

        return jsonify({
            "error": "Coupon code not found or already redeemed",
            "success": False
        }), 400
    except Exception as e:
        return jsonify({
            "error": "Internal Server error",
            "success": False
        }), 500

def redeem_offer(data, user):
    try:
        off_percent = data.get("off_percent")
        product_id = data.get("product_id")

        if not off_percent or not product_id:
            logger.warning("Missing parameters for offer redemption")
            return jsonify({'error': 'off_percent and product_id are required'}), 400

        offer = ProductOffer.objects(admin_uid=user.admin_uid).first()
        if not offer:
            return jsonify({'error': 'No offers available'}), 404

        for o in offer.offers:
            if o['expiry_date'] < datetime.datetime.now():
                continue
            if o['product_uid'] == product_id:
                prod = Product.objects(admin_uid=user.admin_uid).first()
                if not prod:
                    return jsonify({'error': 'Product list not found'}), 404

                for p in prod.products:
                    if p['product_uid'] == product_id:
                        amt = p['original_amt']
                        disc_amt = round(amt * off_percent / 100, 2)
                        return jsonify({
                            "message": f"Congratulations! You have claimed this offer on {p['product_name']}, "
                                       f"you'll get Rs.{disc_amt} off on this product.",
                            "success": True
                        }), 200

                return jsonify({"message": "Failed to claim this offer", "success": False}), 400
            return jsonify({
                            "message": f"Congratulations! You have claimed this offer on {p['product_name']}, "
                                       f"you'll get Rs.{disc_amt} off on this product.",
                            "success": True
                        }), 200
    except Exception as e:
     return jsonify({"error": f"Failed to claim this offer as :  {str(e)}", "success": False}), 400
    
def redeem_exciting_prize(data, user):
    prize_id = data.get("prize_id")
    user_id = data.get("user_id")

    if not prize_id:
        return jsonify({'error': 'prize_id is required'}), 400

    prize_data = AdminPrizes.objects(admin_uid=user.admin_uid).first()
    if not prize_data:
        return jsonify({'message': 'No prizes available'}), 404

    for prize in prize_data.prizes:
        if prize['prize_id'] != prize_id:
            continue

        product_id = prize['product_uid']
        prod = Product.objects(admin_uid=user.admin_uid).first()

        if not prod:
            return jsonify({'message': 'Product list not found'}), 404

        for p in prod.products:
            if p['product_uid'] == product_id:
                reward = Reward.objects(user_id=user_id).first()
                required_meteors = prize['required_meteors']
                if not reward:
                    return jsonify({'error': 'Reward data not found'}), 404

                if reward.current_meteors < required_meteors:
                    needed = required_meteors - reward.current_meteors
                    return jsonify({
                        "message": f"You need {needed} more meteors to unlock this prize.",
                        "success": False
                    }), 400
                if reward.current_meteors > required_meteors:
                    reward.update(
                        inc__redeemed_meteors = required_meteors,
                        dec__current_meteors = required_meteors
                    )
                    

                    return jsonify({
                        "congrats_text": "Congratulations! You have claimed your Prize",
                        "success": True
                    }), 200

    return jsonify({"message": "Prize not found or not eligible", "success": False}), 400

















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


# def redeem(card_type):
#     try:
#         data = request.get_json()
#         user_id = data.get('user_id')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        user = User.objects(user_id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if card_type == "discount-coupon":
            return redeem_discount_coupon(data, user)

        elif card_type == "offers":
            return redeem_offer(data, user)

        elif card_type == "exciting-prizes":
            return redeem_exciting_prize(data, user)

        else:
            return jsonify({'error': 'Invalid card_type'}), 400

    except Exception as e:
        logger.exception(f"Exception during voucher redemption: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def redeem_discount_coupon(data, user):
    user_id = user.user_id
    coupon_code = data.get('coupon_code')

    if not coupon_code:
        logger.warning("Missing coupon_code in redeem request")
        return jsonify({'error': 'coupon_code is required'}), 400

    reward = Reward.objects(user_id=user_id).first()
    if not reward:
        logger.error(f"Reward not found for user_id: {user_id}")
        return jsonify({'error': 'Reward profile not updated'}), 404

    for coupon in reward.discount_coupons:
        if coupon.get('coupon_code') == coupon_code:
            expiry = coupon.get('expiry_date')
            if expiry and expiry < datetime.datetime.now():
                return jsonify({"message": "This coupon has expired", "success": False}), 400

            coupon['redeemed'] = True
            reward.update(
                pull__discount_coupons={"coupon_code": coupon_code},
                dec__unused_vouchers=1,
                inc__used_vouchers=1
            )
            reward.save()

            return jsonify({
                "congrats_text": "Congratulations! You have claimed your Discount Voucher",
                "success": True
            }), 200

    return jsonify({
        "error": "Coupon code not found or already redeemed",
        "success": False
    }), 400


def redeem_offer(data, user):
    try:
        off_percent = data.get("off_percent")
        product_id = data.get("product_id")

        if not off_percent or not product_id:
            logger.warning("Missing parameters for offer redemption")
            return jsonify({'error': 'off_percent and product_id are required'}), 400

        offer = Offer.objects(admin_uid=user.admin_uid).first()
        if not offer:
            return jsonify({'error': 'No offers available'}), 404

        for o in offer.offers:
            if o['expiry_date'] < datetime.datetime.now():
                continue
            if o['product_uid'] == product_id:
                prod = Product.objects(admin_uid=user.admin_uid).first()
                if not prod:
                    return jsonify({'error': 'Product list not found'}), 404

                for p in prod.products:
                    if p['product_uid'] == product_id:
                        amt = p['original_amt']
                        disc_amt = round(amt * off_percent / 100, 2)
                        return jsonify({
                            "message": f"Congratulations! You have claimed this offer on {p['product_name']}, "
                                       f"you'll get Rs.{disc_amt} off on this product.",
                            "success": True
                        }), 200

            return jsonify({"message": "Failed to claim this offer", "success": False}), 400
    except Exception as e:
     return jsonify({"message": f"Failed to claim this offer as {str(e)}", "success": False}), 400


def redeem_exciting_prize(data, user):
    prize_id = data.get("prize_id")
    user_id = data.get("user_id")

    if not prize_id:
        return jsonify({'error': 'prize_id is required'}), 400

    prize_data = AdminPrizes.objects(admin_uid=user.admin_uid).first()
    if not prize_data:
        return jsonify({'error': 'No prizes available'}), 404

    for prize in prize_data.prizes:
        if prize['prize_id'] != prize_id:
            continue

        product_id = prize['product_uid']
        prod = Product.objects(admin_uid=user.admin_uid).first()

        if not prod:
            return jsonify({'error': 'Product list not found'}), 404

        for p in prod.products:
            if p['product_uid'] == product_id:
                reward = Reward.objects(user_id=user_id).first()
                required_meteors = prize['required_meteors']
                if not reward:
                    return jsonify({'error': 'Reward data not found'}), 404

                if reward.current_meteors < required_meteors:
                    needed = required_meteors - reward.current_meteors
                    return jsonify({
                        "error": f"You need {needed} more meteors to unlock this prize.",
                        "success": False
                    }), 400
                if reward.current_meteors > required_meteors:
                    reward.update(
                        inc__redeemed_meteors = required_meteors,
                        dec__current_meteors = required_meteors
                    )

                    reward.reward_history.append({"reward_type" : "exciting_prizes",
                                                  "used_meteors" : required_meteors,
                                                  "date" : datetime.datetime.now().strftime('%d-%m-%y')})

                    return jsonify({
                        "congrats_text": "Congratulations! You have claimed your Prize",
                        "success": True
                    }), 200

    return jsonify({"message": "Prize not found or not eligible", "success": False}), 400



# def redeem(card_type):
#     try:
#         data = request.get_json()
#         user_id = data.get('user_id')
#         user = User.objects(user_id = user_id).first()
#
#         if card_type == "discount-coupon":
#             coupon_code = data.get('coupon_code')
#             print(coupon_code)
#
#             if not user_id or not coupon_code:
#                 logger.warning("Missing required parameters in redeem request")
#                 return jsonify({'error': 'user_id and coupon_code are required'}), 400
#
#             reward = Reward.objects(user_id=user_id).first()
#             if not reward:
#                 logger.error(f"Reward not found for user_id: {user_id}")
#                 return jsonify({'error': 'Reward profile not updated'}), 404
#
#             won_coupons = reward.discount_coupons
#
#             for coupon in won_coupons:
#                 print(coupon)
#                 expiry = coupon.get('expiry_date')
#                 # if expiry < datetime.datetime.now():
#                 #     return jsonify({"message": "This Coupon  has expired", "success": False}), 400
#                 if coupon.get('voucher_code') == coupon_code:
#                     coupon['redeem'] = True
#                     reward.update(
#                         pull__discount_coupons={"voucher_code": coupon_code}
#                     )
#
#                     break
#
#                 reward.update(
#                     dec__unused_vouchers=1,
#                     inc__used_vouchers=1
#                 )
#                 reward.save()
#
#                 return jsonify({
#                     "congrats_text": "Congratulations! You have claimed your Discount Voucher",
#                     "success": True
#                 }), 200
#             return jsonify({
#                     "error": "Something went Wrong",
#                     "success": False
#                 }), 400
#         try:
#             if card_type == "offers":
#                 off_percent = data.get("off_percent")
#                 product_id = data.get("product_id")
#
#                 if not user_id or not off_percent or not product_id:
#                     logger.warning("Missing required parameters in redeem request")
#                     return jsonify({'error': 'Missing required data.'}), 400
#
#                 offer = Offer.objects(admin_uid = user.admin_uid).first()
#                 if offer:
#                     for o in offer.offers:
#                         if o['expiry_date'] < datetime.datetime.now():
#                             return jsonify({"message" :"This offer is not active at the moment",
#                                             "success" : False}), 400
#                         if o['product_id'] == product_id:
#                             prod = Product.objects(admin_uid = user.admin_uid).first()
#                             for p in prod.products:
#                                 if p['uid'] == product_id:
#                                     amt = p['original_amt']
#                                     disc_amt = amt * off_percent/100
#                                     return jsonify({"message" : f"Congratulations! You have claimed this offer on {p['product_name']}, you'll get Rs.{disc_amt}"
#                                                                 f"off on this product.",
#                                                     "success" : True}), 200
#         except Exception as e:
#
#                 return jsonify({"message" : "Failed to claim this offer",
#                                         "success" : False}), 400
#
#         if card_type == "exciting-prizes":
#             required = data.get("meteors_to_unlock")
#             prize_id = data.get("prize_id")
#
#
#             if not user_id :
#                 logger.warning("Missing required parameters in redeem request")
#                 return jsonify({'error': 'Missing required data.'}), 400
#
#             find_prize = AdminPrizes.objects(admin_uid=user.admin_uid).first()
#             if find_prize:
#                 for o in find_prize.prizes:
#                     if o['prize_id'] == prize_id:
#                         return jsonify({"message": "This offer is not active at the moment",
#                                         "success": False}), 400
#                     product_id = o['product_id']
#                     prod = Product.objects(admin_uid=user.admin_uid).first()
#                     for p in prod.products:
#                         if p['uid'] == product_id:
#                             required_meteor = p['required_meteors']
#                             reward = Reward.objects(user_id = user_id).first()
#                             if required_meteor > reward.current_meteors:
#                                 return jsonify({"message" : f"You need {required_meteor - reward.current_meteors} more meteors to unlock this prize.",
#                                                 "success" : False }), 400
#
#                         return jsonify({"message": "Failed to claim this offer",
#                                         "success": False}), 400
#
#             return jsonify({
#                 "congrats_text": "Congratulations! You have claimed your Prize",
#                 "success": True
#             }), 200
#
#     except Exception as e:
#         logger.exception(f"Exception during voucher redemption: {str(e)}")
#         return jsonify({'error': 'Internal server error'}), 500