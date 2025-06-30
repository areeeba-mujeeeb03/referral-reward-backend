from flask import jsonify
from main_app.utils.user.string_encoding import generate_encoded_string

def encode_data():
    try:
        data = {
            "total_participants": "1024",
            "referral_leads": "1024",
            "successful_referrals": "1024",
            "total_referrals": "1024"
        }

        result = generate_encoded_string(data)

        return jsonify({
            "success": True,
            "original_string": result["original_string"],
            "final_string": result["final_string"],
            "parts": result["parts"]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
