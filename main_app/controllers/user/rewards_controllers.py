from flask import jsonify
from main_app.models.admin.discount_coupon_model import ProductDiscounts
from main_app.models.admin.error_model import Errors
from main_app.models.admin.galaxy_model import Galaxy, GalaxyProgram
from main_app.models.user.reward import Reward, Milestone, Galaxy
from main_app.models.admin.product_model import Product
import datetime
import logging
import random
from main_app.models.user.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_planet_and_galaxy(user_id):
    try:
        reward = Reward.objects(user_id=user_id).first()
        user = User.objects(user_id=user_id).first()

        if not reward:
            return jsonify({"message": "User reward not found", "success": False}), 404

        galaxy_program = GalaxyProgram.objects(admin_uid=user.admin_uid, program_id=user.program_id).first()

        total_meteors = reward.total_meteors_earned
        galaxy_or_milestone_unlocked = False
        update_messages = []
        current_active_galaxy = None

        for program_galaxy in galaxy_program.galaxies:
            user_galaxy = None
            for g in reward.galaxies:
                if g.galaxy_name == program_galaxy.galaxy_name:
                    user_galaxy = g.galaxy_name
                    break

            if not user_galaxy:
                first_milestone = program_galaxy.milestones[0]
                if total_meteors >= first_milestone.meteors_required_to_unlock:
                    unlocked_milestone = Milestone(
                        milestone_name=first_milestone.milestone_name,
                        milestone_status='unlocked'
                    )
                    new_galaxy = Galaxy(
                        galaxy_name=program_galaxy.galaxy_name,
                        milestones=[unlocked_milestone]
                    )
                    reward.galaxies.append(new_galaxy)
                    reward.total_meteors_earned += first_milestone.milestone_reward
                    reward.reward_history.append({
                        "reward_type": 'milestone_reward',
                        "date": datetime.datetime.now(),
                        "meteor": first_milestone.milestone_reward,
                        "transaction_type": "credit"
                    })

                    galaxy_or_milestone_unlocked = True
                    update_messages.append(f"Unlocked galaxy '{program_galaxy.galaxy_name}' with milestone '{first_milestone.milestone_name}'")
                    current_active_galaxy = program_galaxy.galaxy_name
                    break
            else:
                unlocked_names = [m.milestone_name for m in user_galaxy.milestones]
                for prog_milestone in program_galaxy.milestones:
                    if prog_milestone.milestone_name not in unlocked_names:
                        if total_meteors >= prog_milestone.meteors_required_to_unlock:
                            new_milestone = Milestone(
                                milestone_name=prog_milestone.milestone_name,
                                milestone_status='unlocked'
                            )
                            user_galaxy.milestones.append(new_milestone)
                            reward.total_meteors_earned += prog_milestone.milestone_reward
                            reward.reward_history.append({
                                "reward_type": 'milestone_reward',
                                "date": datetime.datetime.now(),
                                "meteor": prog_milestone.milestone_reward,
                                "transaction_type": "credit"
                            })

                            galaxy_or_milestone_unlocked = True
                            update_messages.append(f"Unlocked milestone '{prog_milestone.milestone_name}' in galaxy '{program_galaxy.galaxy_name}'")
                            current_active_galaxy = program_galaxy.galaxy_name
                            break
                        else:
                            break

                if galaxy_or_milestone_unlocked:
                    break

        if not current_active_galaxy:
            if reward.galaxies:
                current_active_galaxy = reward.galaxies[-1].galaxy_name

        galaxy_display = []
        if current_active_galaxy:
            pg = next((g for g in galaxy_program.galaxies if g.galaxy_name == current_active_galaxy), None)
            user_g = next((g for g in reward.galaxies if g.galaxy_name == current_active_galaxy), None)

            if pg:
                galaxy_entry = {
                    "galaxy_name": pg.galaxy_name,
                    "milestones": []
                }

                user_milestone_names = [m.milestone_name for m in user_g.milestones] if user_g else []

                for pm in pg.milestones:
                    milestone_entry = {
                        "milestone_name": pm.milestone_name,
                        "milestone_status": "unlocked" if pm.milestone_name in user_milestone_names else "locked"
                    }
                    galaxy_entry["milestones"].append(milestone_entry)

                galaxy_display.append(galaxy_entry)

        if galaxy_or_milestone_unlocked:
            reward.save()

        return jsonify({
            "total_meteors": reward.total_meteors_earned,
            "meteors": reward.current_meteors,
            "galaxies": galaxy_display,
            "success": True
        }), 200

    except Exception as e:
        return jsonify({
            "message": f"Error: {str(e)}",
            "success": False
        }), 500
        

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

        products = ProductDiscounts.objects(admin_uid = user.admin_uid, program_id = user.program_id).first()

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
            "coupon_code": won_product['coupon_code'],
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
        reward.reward_history.append({
            "earned_by_action": "voucher_won",
            "voucher_code": won_product.coupon_code,
            "expiry": now,
            "meteors" : None
        })
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