import datetime
from flask import request, jsonify
from bson import ObjectId
import logging
from main_app.models.admin.admin_model import Admin
from main_app.models.admin.advertisment_card_model import AdvertisementCardItem, AdminAdvertisementCard
from main_app.models.admin.campaign_model import Campaign
from main_app.models.admin.email_model import EmailTemplate
from main_app.models.admin.galaxy_model import GalaxyProgram, Milestone, Galaxy
from main_app.models.admin.help_model import FAQ
from main_app.models.admin.how_it_work_model import HowItWork
from main_app.models.admin.links import AppStats, ReferralReward, Link
from main_app.models.admin.participants_model import Participants
from main_app.models.admin.product_model import Product 
from main_app.models.admin.product_offer_model import Offer
from main_app.models.admin.perks_model import Perks
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

        # Required basic fields
        admin_uid = data.get("admin_uid")
        campaign_name = data.get("campaign_name")
        base_url = data.get("base_url")
        image = data.get("image")
        access_token = data.get("mode")
        session_id = data.get("log_alt")

        if not all([admin_uid, access_token, session_id, campaign_name]):
            return jsonify({"message": "Missing required fields", "success": False}), 400

        admin = Admin.objects(admin_uid=admin_uid).first()
        if not admin:
            return jsonify({"success": False, "message": "User does not exist"}), 404

        if admin.access_token != access_token:
            return jsonify({"success": False, "message": "Invalid access token"}), 401

        if admin.session_id != session_id:
            return jsonify({"success": False, "message": "Session mismatch or invalid session"}), 403

        if getattr(admin, "expiry_time", None) and datetime.datetime.now() > admin.expiry_time:
            return jsonify({"success": False, "message": "Access token has expired"}), 401

        # Check if campaign name exists
        if any(c["program_name"].strip().lower() == campaign_name.strip().lower() for c in admin.all_campaigns):
            return jsonify({"message": "Campaign with this name already exists", "success": False}), 400

        # Create campaign
        camp = Campaign(
            admin_uid=admin_uid,
            program_name=campaign_name,
            total_participants=0,
            base_url=base_url,
            image=image
        )

        # Update Admin
        admin.all_campaigns.append({
            "program_name": campaign_name,
            "program_id": camp.program_id,
            "base_url": base_url,
            "image": image
        })

        # ReferralReward validation
        cr = data.get("conversion_rates", {})
        if not all(k in cr for k in ["meteors_to_stars", "stars", "stars_to_currency", "currency"]):
            return jsonify({"error": "Invalid conversion rates format"}), 400

        referral_fields = ["refer_reward_type", "referrer_reward", "invitee_reward", "invitee_reward_type"]
        if not all(data.get(field) for field in referral_fields):
            return jsonify({"error": "Missing referral reward fields"}), 400


        # Invite Link
        special_link = Link(
            admin_uid=admin_uid,
            program_id=camp.program_id,
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            invitation_link=data.get("link"),
            created_at=datetime.datetime.now(),
            referrer_reward_type=data.get("refer_reward_type"),
            referrer_reward_value=data.get("referrer_reward_value"),
            referee_reward_type=data.get("referee_reward_type"),
            referee_reward_value=data.get("referee_reward_value"),
            reward_condition=data.get("reward_condition"),
            success_reward=data.get("success_reward"),
            active=data.get("active", False)
        )

        # AppStats
        stats = AppStats.objects(admin_uid=admin_uid, program_id=camp.program_id).first()
        if not stats:
            stats = AppStats(admin_uid=admin_uid, program_id=camp.program_id, apps=[])

        new_platforms = data.get("platforms", [])
        existing_platforms = {app.get("platform") for app in stats.apps}

        for platform in new_platforms:
            if platform["platform"] not in existing_platforms:
                stats.apps.append({
                    "platform": platform["platform"],
                    "message": platform["message"],
                    "sent": 0, "accepted": 0, "successful": 0
                })
        stats.primary_platform = data.get("primary_platform")

        # How it Works
        how_it_works = HowItWork(
            admin_uid=admin_uid,
            program_id=camp.program_id,
            title1=data.get("title1"),
            desc1=data.get("desc1"),
            title2=data.get("title2"),
            desc2=data.get("desc2"),
            title3=data.get("title3"),
            desc3=data.get("desc3"),
            footer_text=data.get("footer_text")
        )

        # FAQs
        faqs = data.get("faqs", [])
        faq_obj = FAQ(admin_uid=admin_uid, program_id=camp.program_id, categories=faqs)

        # Advertisement Cards
        ads_data = data.get("advertisement_cards", [])
        ad_cards = [
            AdvertisementCardItem(
                title=card["title"],
                description=card["description"],
                button_txt=card["button_txt"],
                image=card["image"]
            ) for card in ads_data
        ]
        AdminAdvertisementCard(
            admin_uid=admin_uid,
            program_id=camp.program_id,
            advertisement_cards=ad_cards
        ).save()
        ##saving Data in Database
        camp.save()
        initialize_admin_data(admin_uid, camp.program_id)
        admin.save()
        how_it_works.save()
        faq_obj.save()
        stats.save()
        special_link.save()

        # GalaxyProgram
        galaxy_program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=camp.program_id).first()
        if not galaxy_program:
            galaxy_program = GalaxyProgram(admin_uid=admin_uid, program_id=camp.program_id, galaxies=[])

        galaxies_data = data.get("galaxies", [])
        existing_names = {g.galaxy_name.lower() for g in galaxy_program.galaxies}

        for galaxy_data in galaxies_data:
            name = galaxy_data.get("galaxy_name")
            milestones_data = galaxy_data.get("milestones", [])

            if not name or name.lower() in existing_names or not milestones_data:
                continue

            milestones = [
                Milestone(
                    milestone_name=m.get("milestone_name"),
                    meteors_required_to_unlock=m.get("meteors_required_to_unlock", 0),
                    milestone_reward=m.get("milestone_reward", 0),
                    milestone_description=m.get("milestone_description", "")
                ) for m in milestones_data
            ]
            galaxy_program.galaxies.append(Galaxy(
                galaxy_id=f"GXY_{len(galaxy_program.galaxies) + 1}",
                galaxy_name=name,
                total_milestones=int(galaxy_data.get("total_milestones")),
                highest_reward=galaxy_data.get("highest_reward"),
                stars_to_be_achieved=galaxy_data.get("stars"),
                milestones=milestones,
                total_meteors_required=milestones[-1]["meteors_required_to_unlock"]
            ))
        galaxy_program.save()
        # Participants rewards
        Participants.objects(admin_uid=admin_uid, program_id=camp.program_id).update(
            login_reward=data.get("login_reward"),
            signup_reward=data.get("signup_reward"),
            signup_reward_type=data.get("signup_reward_type"),
            login_reward_type=data.get("login_reward_type")
        )
        referral_rewards = ReferralReward.objects(admin_uid=admin_uid, program_id=camp.program_id).update_one(
            set__referrer_reward=data["referrer_reward"],
            set__invitee_reward=data["invitee_reward"],
            set__conversion_rates=cr,
            set__referrer_reward_type=data["refer_reward_type"],
            set__invitee_reward_type=data["invitee_reward_type"],
            set__updated_at=datetime.datetime.now(),
            upsert=True
        )


        return jsonify({"message": "Successfully Created a Campaign", "success": True}), 201

    except Exception as e:
        logger.error(f"Failed to initialize campaign: {str(e)}")
        return jsonify({"message": "Failed to add Campaign", "success": False}), 400

def initialize_admin_data(admin_uid, program_id):
    if not Participants.objects(admin_uid=admin_uid, program_id=program_id):
        Participants(admin_uid=admin_uid, program_id=program_id).save()

    if not ReferralReward.objects(admin_uid=admin_uid, program_id=program_id):
        ReferralReward(admin_uid=admin_uid, program_id=program_id).save()

    if not Product.objects(admin_uid=admin_uid, program_id=program_id):
        Product(admin_uid=admin_uid, program_id=program_id).save()

    if not SOffer.objects(admin_uid=admin_uid, program_id=program_id):
        SOffer(admin_uid=admin_uid, program_id=program_id).save()

    if not Offer.objects(admin_uid=admin_uid, program_id=program_id):
         Offer(admin_uid=admin_uid, program_id=program_id).save()

    if not AdminPrizes.objects(admin_uid=admin_uid, program_id=program_id):
         AdminPrizes(admin_uid=admin_uid, program_id=program_id).save()

    if not Perks.objects(admin_uid=admin_uid, program_id=program_id):
         Perks(admin_uid=admin_uid, program_id=program_id).save()
         
    if not ProductDiscounts.objects(admin_uid=admin_uid, program_id=program_id):
        ProductDiscounts(admin_uid=admin_uid, program_id=program_id).save()

    return "done", 200

def serialize_mongo(data):
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, dict):
        return {key: serialize_mongo(value) for key, value in data.items()}
    if isinstance(data, list):
        return [serialize_mongo(item) for item in data]
    return data

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

        sharing_apps = AppStats.objects(admin_uid=admin_uid, program_id=program_id).first()
        sharing_apps_info = sharing_apps.to_mongo().to_dict() if sharing_apps else {}
        models_to_fetch = [
            Campaign,
            ReferralReward,
            GalaxyProgram,
            AppStats,
            AdminAdvertisementCard,
            HowItWork,
            FAQ,
            Link,
            Participants

        ]
        result = []
        for model in models_to_fetch:
            doc = model.objects(admin_uid=admin_uid, program_id=program_id).first()
            if doc:
                j_doc = doc.to_mongo().to_dict()
                j_doc.pop('_id', None)
                result.append(j_doc)
                logger.info(f"Data Fetched from {model} successfully")

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

        # Update campaign fields
        campaign.program_name = data.get("campaign_name", campaign.program_name)
        campaign.base_url = data.get("base_url", campaign.base_url)
        campaign.image = data.get("image", campaign.image)
        campaign.save()

        # Sync with admin
        for c in admin.all_campaigns:
            if c.get("program_id") == program_id:
                c["program_name"] = campaign.program_name
                c["base_url"] = campaign.base_url
                c["image"] = campaign.image
        admin.save()

        # Update ReferralReward if exists
        conversion_rates = data.get("conversion_rates", {})
        if not all(k in conversion_rates for k in ["meteors_to_stars", "stars", "stars_to_currency", "currency"]):
            return jsonify({"error": "Invalid conversion_rates format"}), 400

        referral_reward = ReferralReward.objects(admin_uid=admin_uid, program_id=program_id).first()
        if referral_reward:
            referral_reward.update(
                set__referrer_reward=data.get("referrer_reward"),
                set__invitee_reward=data.get("invitee_reward"),
                set__conversion_rates=conversion_rates,
                set__referrer_reward_type=data.get("refer_reward_type"),
                set__invitee_reward_type=data.get("invitee_reward_type"),
                set__updated_at=datetime.datetime.now()
            )

        # Update Participants if exists
        participant = Participants.objects(admin_uid=admin_uid, program_id=program_id).first()
        if participant:
            participant.update(
                set__signup_reward=data.get("signup_reward"),
                set__signup_reward_type=data.get("signup_reward_type"),
                set__login_reward=data.get("login_reward"),
                set__login_reward_type=data.get("login_reward_type")
            )

        # Handle link update or create
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

        # Update AppStats
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

        # Update HowItWorks
        title1 = data.get("title1")
        desc1 = data.get("desc1")
        title2 = data.get("title2")
        desc2 = data.get("desc2")
        title3 = data.get("title3")
        desc3 = data.get("desc3")
        footer_text = data.get("footer_text")

        how_it_works = HowItWork.objects(admin_uid=admin_uid, program_id=program_id).first()
        if how_it_works:
            how_it_works.update(
                title1=title1,
                desc1=desc1,
                title2=title2,
                desc2=desc2,
                title3=title3,
                desc3=desc3,
                footer_text=footer_text
            )
        else:
            how_it_works = HowItWork(
                admin_uid=admin_uid,
                program_id=program_id,
                title1=title1,
                desc1=desc1,
                title2=title2,
                desc2=desc2,
                title3=title3,
                desc3=desc3,
                footer_text=footer_text
            )
            how_it_works.save()

        # Update Galaxy Program
        galaxies_data = data.get("galaxies", [])
        galaxy_program = GalaxyProgram.objects(admin_uid=admin_uid, program_id=program_id).first()
        if not galaxy_program:
            galaxy_program = GalaxyProgram(admin_uid=admin_uid, program_id=program_id, galaxies=[])
        else:
            galaxy_program.galaxies = []

        for i, galaxy_data in enumerate(galaxies_data, start=1):
            milestones = [
                Milestone(
                    milestone_name=m.get("milestone_name"),
                    meteors_required_to_unlock=m.get("meteors_required_to_unlock", 0),
                    milestone_reward=m.get("milestone_reward", 0),
                    milestone_description=m.get("milestone_description", "")
                ) for m in galaxy_data.get("milestones", [])
            ]

            galaxy_program.galaxies.append(Galaxy(
                galaxy_id=f"GXY_{i}",
                galaxy_name=galaxy_data.get("galaxy_name"),
                total_milestones=galaxy_data.get("total_milestones"),
                highest_reward=galaxy_data.get("highest_reward"),
                stars_to_be_achieved=galaxy_data.get("stars"),
                milestones=milestones
            ))
        galaxy_program.save()

        # Advertisement cards (assuming you meant to update it)
        ad_card = AdminAdvertisementCard.objects(admin_uid=admin_uid, program_id=program_id).first()
        if ad_card:
            ad_card_data = data.get("advertisement_cards", [])
            ad_card.advertisement_cards = ad_card_data
            ad_card.save()

        return jsonify({"success": True, "message": "Campaign updated successfully"}), 200

    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        return jsonify({"success": False, "message": "Failed to update campaign"}), 500


def delete_campaign(program_id):
    try:
        logger.info("Starting deleting Campaign API")
        data = request.get_json()
        admin_uid = data.get("admin_uid")

        if not admin_uid or not program_id:
            return jsonify({"success": False, "message": "admin_uid and program_id are required"}), 400
        admin = Admin.objects(admin_uid = admin_uid).first()
        admin.update(
            pull__all_campaigns = {'program_id' :program_id}
        )
        models_to_delete = [
            Campaign,
            ReferralReward,
            Participants,
            GalaxyProgram,
            AppStats,
            AdminAdvertisementCard,
            HowItWork,
            FAQ
        ]

        for model in models_to_delete:
            doc = model.objects(admin_uid=admin_uid, program_id=program_id).first()
            if doc:
                doc.delete()
                logger.info(f"Campaign data removed from {model} successfully")

        return jsonify({"success": True, "message": "Campaign deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        return jsonify({"success": False, "message": "Failed to delete campaign"}), 500

def all_products(program_id):
    try:
        data = request.get_json()
        admin_uid = data.get("admin_uid")
        if not admin_uid:
            return jsonify({"success": False, "message": "admin_uid is required"}), 400

        models_to_fetch = [Product,Offer,AdminPrizes,Perks,ProductDiscounts]
        result = []
        for model in models_to_fetch:
            doc = model.objects(admin_uid=admin_uid, program_id=program_id).first()
            if doc:
                j_doc = doc.to_mongo().to_dict()
                j_doc.pop('_id', None)
                result.append(j_doc)
                logger.info(f"Data Fetched from {model} successfully")

        return jsonify({"success": True, "data": result}), 200
    except Exception as e:
        logger.error(f"Error fetching campaign products: {e}")
        return jsonify({"success": False, "message": "Error fetching campaign products"}), 500