from flask import jsonify
from main_app.utils.user.string_encoding import generate_encoded_string

def encode_data():
    try:
        data = {
            "total_participants": "1024",
            "referral_leads": "1024",
            "successful_referrals": "1024",
            "total_referrals": "1024",
            "converted_referrals": "24",
            "total_used_coupons": "24",
            "total_rewards_given": "24",
        }

        fields_to_encode = ["total_participants","referral_leads","successful_referrals","total_referrals","converted_referrals","total_used_coupons","total_rewards_given"]

        result = generate_encoded_string(data,fields_to_encode)

        return result

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



# from flask import jsonify
# from main_app.utils.user.string_encoding import generate_encoded_string
# from main_app.models.admin.dashboard_model import dashboard_data
#
# def encode_data():
#     try:
#         # Fetch the document (latest one as an example)
#         stats = ReferralStats.objects().order_by('-created_at').first()
#
#         if not stats:
#             return jsonify({"success": False, "message": "No data found"}), 404
#
#         # Convert the document to a dictionary
#         data = stats.to_mongo().to_dict()
#
#         # Define which fields to encode
#         fields_to_encode = [
#             "total_participants",
#             "referral_leads",
#             "successful_referrals",
#             "total_referrals",
#             "converted_referrals",
#             "total_used_coupons",
#             "total_rewards_given"
#         ]
#
#
#         result = generate_encoded_string(data, fields_to_encode)
#
#         return result
#
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500
