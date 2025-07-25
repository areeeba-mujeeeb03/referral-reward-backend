import datetime
from flask import request, jsonify
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.campaign_model import Campaign
from main_app.models.admin.discount_coupon_model import ProductDiscounts
from main_app.models.admin.galaxy_model import GalaxyProgram, Milestone, Galaxy
from main_app.models.admin.links import AppStats, ReferralReward, Link
from main_app.models.admin.participants_model import Participants
from main_app.models.admin.product_model import Product
from main_app.models.admin.product_offer_model import Offer
from main_app.models.admin.perks_model import ExclusivePerks, Perks
from main_app.models.admin.prize_model import AdminPrizes
from main_app.models.admin.discount_coupon_model import ProductDiscounts
from main_app.models.admin.special_offer_model import SOffer

# Configure logging for better debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_program_id(admin_uid):
    prog_doc = Admin.objects(admin_uid=admin_uid).first()
    count = 1
    if prog_doc:
        for program in prog_doc.all_campaigns:
            if program:
                  count = len(prog_doc.all_campaigns) + 1
    else:
        count = 1
    return f"PROG_{str(count).zfill(2)}"

def create_new_campaign():
    try:
        logger.info("Initializing New Campaign")
        data = request.get_json()

        ##Create campaign
        admin_uid = data.get("admin_uid")
        campaign_name = data.get("campaign_name")
        subtitle = data.get("subtitle")
        base_url = data.get("url")
        image = data.get("image")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        admin = Admin.objects(admin_uid=admin_uid).first()

        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404
        #
        # if not admin_uid or not access_token or not session_id:
        #     return jsonify({"message": "Missing required fields", "success": False}), 400
        #
        # if admin.access_token != access_token:
        #     return ({"success": False,
        #              "message": "Invalid access token"}), 401
        #
        # if admin.session_id != session_id:
        #     return ({"success": False,
        #              "message": "Session mismatch or invalid session"}), 403
        #
        # if hasattr(admin, 'expiry_time') and admin.expiry_time:
        #     if datetime.datetime.now() > admin.expiry_time:
        #         return jsonify({"success": False, "message": "Access token has expired"}), 401

        find = Campaign.objects(admin_uid = admin_uid)
        for campa in find:
            if campa['program_name'] == campaign_name:
                return jsonify({"message": "Campaign with this name already exists", "success": False}), 400

        camp = Campaign(
            admin_uid = admin_uid,
            program_name = campaign_name,
            total_participants = 0,
            base_url = base_url,
            image = image
        )

        for campaign in admin.all_campaigns:
            if campaign['program_name'].strip().lower() == campaign_name.strip().lower():
                return jsonify({"message": "Campaign with this name already exists", "success": False}), 400

        #referral Rewards
        required_fields = ['refer_reward_type','referrer_reward','invitee_reward' ,'invitee_reward_type', 'conversion_rates']

        if not all(required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # if type('referrer_reward') != int and type('invitee_reward') != int:
        #     return jsonify({"message": "The type of referral and invitee reward must be an integer"})

        cr = data['conversion_rates']
        if not all(k in cr for k in ["meteors_to_stars", "stars", "stars_to_currency", "currency"]):
            return jsonify({"error": "Invalid conversion rates format"}), 400

        ## Add Bonus rewards
        signup_reward = data.get("signup_reward")
        signup_reward_type = data.get("signup_reward_type")
        login_reward = data.get("login_reward")
        login_reward_type = data.get("login_reward_type")

        ## Special Link Generation
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        referrer_reward_type = data.get("refer_reward_type")
        referrer_reward_value = data.get("referrer_reward_value")
        referee_reward_type = data.get("referee_reward_type")
        referee_reward_value = data.get("referee_reward_value")
        reward_condition = data.get("reward_condition")
        success_reward = data.get("success_reward")
        invite_link = data.get("link")
        active = data.get("active", False)

        existing_link = Link.objects(admin_uid=admin_uid, program_id=camp.program_id).first()
        if existing_link:
            existing_link.update(
                start_date=start_date,
                end_date=end_date,
                invitation_link=invite_link,
                created_at=datetime.datetime.now(),
                referrer_reward_type=referrer_reward_type,
                referrer_reward_value=referrer_reward_value,
                referee_reward_type=referee_reward_type,
                referee_reward_value=referee_reward_value,
                reward_condition=reward_condition,
                success_reward=success_reward,
                active=active
            )

        datas = Link(
            admin_uid=admin_uid,
            program_id=camp.program_id,
            start_date=start_date,
            end_date=end_date,
            invitation_link=invite_link,
            created_at=datetime.datetime.now(),
            referrer_reward_type=referrer_reward_type,
            referrer_reward_value=referrer_reward_value,
            referee_reward_type=referee_reward_type,
            referee_reward_value=referee_reward_value,
            reward_condition=reward_condition,
            success_reward=success_reward,
            active=active
        )

        ##Sharing Apps Data
        platforms = data.get("platforms", [])
        primary_platform = data.get("primary_platform")

        stats = AppStats.objects(admin_uid=admin_uid, program_id=camp.program_id).first()

        if not stats:
            stats = AppStats(admin_uid=admin_uid, program_id=camp.program_id, apps=[])

        existing_platforms = {}
        for app in stats.apps:
            platform = app.get("platform")
            if platform:
                existing_platforms[platform] = app

        for platform in platforms:
            if platform['platform'] not in existing_platforms:
                stats.apps.append({
                    "platform": platform['platform'],
                    "message": platform['message'],
                    "sent": 0,
                    "accepted": 0,
                    "successful": 0
                })

        if primary_platform:
            stats.primary_platform = primary_platform

        galaxies_data = data.get("galaxies", [])

        galaxy_program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=camp.program_id).first()

        ## save Data
        new_campaign = {
            "program_name": campaign_name,
            "program_id": camp.program_id,
            "base_url": base_url,
            "image" : image
        }

        admin.all_campaigns.append(new_campaign)
        camp.save()
        admin.save()
        initialize_admin_data(admin_uid, camp.program_id)
        ReferralReward.objects(admin_uid=admin_uid, program_id=camp.program_id).update_one(
            set__referrer_reward=data['referrer_reward'],
            set__invitee_reward=data['invitee_reward'],
            set__conversion_rates=data['conversion_rates'],
            set__referrer_reward_type = data['refer_reward_type'],
            set__invitee_reward_type = data['invitee_reward_type'],
            set__updated_at=datetime.datetime.now(),
            upsert=True
        )
        Participants.objects(admin_uid=admin_uid, program_id=camp.program_id).update(
            login_reward=login_reward,
            signup_reward=signup_reward,
            signup_reward_type = signup_reward_type,
            login_reward_type = login_reward_type
        )
        datas.save()
        stats.save()
        print(galaxies_data)

        if not galaxy_program:
            galaxy_program = GalaxyProgram(
                admin_uid=admin_uid,
                program_id=camp.program_id,
                galaxies=[]
            )

        existing_galaxy_names = {g.galaxy_name.lower() for g in galaxy_program.galaxies}

        for galaxy_data in galaxies_data:
            galaxy_name = galaxy_data.get("galaxy_name")
            if not galaxy_name or galaxy_name.lower() in existing_galaxy_names:
                continue

            total_milestones = galaxy_data.get("total_milestones")
            highest_reward = galaxy_data.get("highest_reward")
            stars = galaxy_data.get("stars")
            milestones_data = galaxy_data.get("milestones", [])

            milestone_objects = []
            for m in milestones_data:
                milestone = Milestone(
                    milestone_name=m.get("milestone_name"),
                    meteors_required_to_unlock=m.get("meteors_required_to_unlock", 0),
                    milestone_reward=m.get("milestone_reward", 0),
                    milestone_description=m.get("milestone_description", "")
                )
                milestone_objects.append(milestone)

            galaxy_id = f"GXY_{len(galaxy_program.galaxies) + 1}"

            new_galaxy = Galaxy(
                galaxy_id=galaxy_id,
                galaxy_name=galaxy_name,
                total_milestones=total_milestones,
                highest_reward=highest_reward,
                stars_to_be_achieved=stars,
                milestones=milestone_objects
            )

            galaxy_program.galaxies.append(new_galaxy)
            existing_galaxy_names.add(galaxy_name.lower())
        galaxy_program.save()

        return jsonify({"message": "Successfully Created a Campaign", "success": True}), 201

    except Exception as e:
        logger.error(f"Failed to initialize campaign as {str(e)}")
        return jsonify({"message": "Failed to add Campaign", "success": False}), 400

def initialize_admin_data(admin_uid, program_id):
    if not Participants.objects(admin_uid=admin_uid, program_id=program_id):
        Participants(admin_uid=admin_uid, program_id=program_id).save()

    if not AppStats.objects(admin_uid=admin_uid, program_id=program_id):
        AppStats(admin_uid=admin_uid, program_id=program_id).save()

    if not ReferralReward.objects(admin_uid=admin_uid, program_id=program_id):
        ReferralReward(admin_uid=admin_uid, program_id=program_id).save()

    if not Product.objects(admin_uid=admin_uid, program_id=program_id):
        Product(admin_uid=admin_uid, program_id=program_id).save()

    if not Product.objects(admin_uid=admin_uid, program_id=program_id):
        Product(admin_uid=admin_uid, program_id=program_id).save()

    if not SOffer.objects(admin_uid=admin_uid, program_id=program_id):
        SOffer(admin_uid=admin_uid, program_id=program_id).save()

    if not Offer.objects(admin_uid=admin_uid, program_id=program_id):
        Offer(admin_uid=admin_uid, program_id=program_id).save()

    if not Perks.objects(admin_uid=admin_uid, program_id=program_id):
        Perks(admin_uid=admin_uid, program_id=program_id).save()

    if not AdminPrizes.objects(admin_uid=admin_uid, program_id=program_id):
        AdminPrizes(admin_uid=admin_uid, program_id=program_id).save()

    if not ProductDiscounts.objects(admin_uid=admin_uid, program_id=program_id):
        ProductDiscounts(admin_uid=admin_uid, program_id=program_id).save()

    return "done", 200

def edit_campaign(program_id):
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        if not admin_uid:
            return jsonify({"success": False, "message": "admin_uid is required"}), 400

        campaign = Campaign.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not campaign:
            return jsonify({"success": False, "message": "Campaign not found"}), 404

        referral_data = ReferralReward.objects(admin_uid=admin_uid, program_id=program_id).first()
        referral_info = referral_data.to_mongo().to_dict() if referral_data else {}

        participant = Participants.objects(admin_uid=admin_uid, program_id=program_id).first()
        participant_info = participant.to_mongo().to_dict() if participant else {}

        galaxy_program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=program_id).first()
        galaxy_info = galaxy_program.to_mongo().to_dict() if galaxy_program else {}

        result = {
            "campaign": {
                "program_name": campaign.program_name,
                "base_url": campaign.base_url,
                "image": campaign.image,
                "program_id": campaign.program_id,
            },
            "referral_reward": referral_info,
            "participant_rewards": participant_info,
            "galaxy_data": galaxy_info
        }

        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        logger.error(f"Error editing campaign: {e}")
        return jsonify({"success": False, "message": "Something went wrong"}), 500


def update_campaign(program_id):
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")

        if not admin_uid or not program_id:
            return jsonify({"success": False, "message": "admin_uid and program_id are required"}), 400

        campaign = Campaign.objects(admin_uid=admin_uid, program_id=program_id).first()
        admin = Admin.objects(admin_uid=admin_uid).first()
        if not campaign or not admin:
            return jsonify({"success": False, "message": "Campaign or Admin not found"}), 404

        campaign.program_name = data.get("campaign_name", campaign.program_name)
        campaign.base_url = data.get("base_url", campaign.base_url)
        campaign.image = data.get("image", campaign.image)
        campaign.save()

        for c in admin.all_campaigns:
            if c.get("program_id") == program_id:
                c["program_name"] = campaign.program_name
                c["base_url"] = campaign.base_url
                c["image"] = campaign.image
        admin.save()

        conversion_rates = data.get("conversion_rates", {})
        if not all(k in conversion_rates for k in ["meteors_to_stars", "stars", "stars_to_currency", "currency"]):
            return jsonify({"error": "Invalid conversion_rates format"}), 400

        ReferralReward.objects(admin_uid=admin_uid, program_id=program_id).update_one(
            set__referrer_reward=data.get("referrer_reward"),
            set__invitee_reward=data.get("invitee_reward"),
            set__conversion_rates=conversion_rates,
            set__referrer_reward_type=data.get("refer_reward_type"),
            set__invitee_reward_type=data.get("invitee_reward_type"),
            set__updated_at=datetime.datetime.now()
        )

        Participants.objects(admin_uid=admin_uid, program_id=program_id).update_one(
            set__signup_reward=data.get("signup_reward"),
            set__signup_reward_type=data.get("signup_reward_type"),
            set__login_reward=data.get("login_reward"),
            set__login_reward_type=data.get("login_reward_type")
        )

        link_data = {
            "start_date": data.get("start_date"),
            "end_date": data.get("end_date"),
            "invitation_link": data.get("link"),
            "referrer_reward_type": data.get("refer_reward_type"),
            "referrer_reward_value": data.get("referrer_reward_value"),
            "referee_reward_type": data.get("referee_reward_type"),
            "referee_reward_value": data.get("referee_reward_value"),
            "reward_condition": data.get("reward_condition"),
            "success_reward": data.get("success_reward"),
            "active": data.get("active", False),
            "created_at": datetime.datetime.now()
        }

        link = Link.objects(admin_uid=admin_uid, program_id=program_id).first()
        if link:
            link.update(**{f"set__{k}": v for k, v in link_data.items()})
        else:
            Link(admin_uid=admin_uid, program_id=program_id, **link_data).save()

        platforms = data.get("platforms", [])
        primary_platform = data.get("primary_platform")

        stats = AppStats.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not stats:
            stats = AppStats(admin_uid=admin_uid, program_id=program_id, apps=[])

        existing_platforms = {app["platform"] for app in stats.apps}
        for platform in platforms:
            if platform["platform"] not in existing_platforms:
                stats.apps.append({
                    "platform": platform["platform"],
                    "message": platform["message"],
                    "sent": 0,
                    "accepted": 0,
                    "successful": 0
                })

        if primary_platform:
            stats.primary_platform = primary_platform
        stats.save()

        galaxies_data = data.get("galaxies", [])
        galaxy_program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not galaxy_program:
            galaxy_program = GalaxyProgram(admin_uid=admin_uid, program_id=program_id, galaxies=[])
        else:
            galaxy_program.galaxies = []

        for idx, galaxy_data in enumerate(galaxies_data, start=1):
            milestones = [
                Milestone(
                    milestone_name=m.get("milestone_name"),
                    meteors_required_to_unlock=m.get("meteors_required_to_unlock", 0),
                    milestone_reward=m.get("milestone_reward", 0),
                    milestone_description=m.get("milestone_description", "")
                ) for m in galaxy_data.get("milestones", [])
            ]

            galaxy_program.galaxies.append(Galaxy(
                galaxy_id=f"GXY_{idx}",
                galaxy_name=galaxy_data.get("galaxy_name"),
                total_milestones=galaxy_data.get("total_milestones"),
                highest_reward=galaxy_data.get("highest_reward"),
                stars_to_be_achieved=galaxy_data.get("stars"),
                milestones=milestones
            ))

        galaxy_program.save()

        initialize_admin_data(admin_uid, program_id)

        return jsonify({"success": True, "message": "Campaign updated successfully"}), 200

    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        return jsonify({"success": False, "message": "Failed to update campaign"}), 500