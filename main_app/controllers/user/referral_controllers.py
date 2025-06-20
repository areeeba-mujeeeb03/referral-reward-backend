import datetime
from main_app.models.user.reward import Reward
from main_app.models.user.referral import Referral

def create_or_update_referrals(referrer_id, referred_user_id):
    referral = Referral.objects(user_id=referrer_id).first()
    reward = Reward.objects(user_id=referrer_id).first()
    date = datetime.datetime.now()

    if referral:
        referral.total_referrals += 1
        referral.referral_earning += 400
        referral.pending_referrals += 1
        referral.all_referrals.append({
            "user_id": referred_user_id,
            "referral_status": "pending",
            "earned_points": 400,
            "referred_on": date
        })
        referral.save()

    if reward:
        reward.total_meteors += 400
        reward.reward_history.append({
            "earned_by_action": "referral",
            "referred_on": date,
            "earned_points": 400,
            "referral_status": "pending",
            "meteor_status": "credited"
        })
        reward.save()

def update_referral_status(referred_user_id):
    referral = Referral.objects(all_referrals__user_id=referred_user_id).first()
    if referral:
        for ref in referral.all_referrals:
            if ref.get("user_id")== referred_user_id:
               ref["referral_status"] = "completed"
            Referral.pending_referrals = max  (0, referral.pending_referrals -1)

        referral.save()
