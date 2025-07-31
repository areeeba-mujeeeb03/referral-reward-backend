import datetime

from flask import request, jsonify

from main_app.models.admin.admin_model import Admin
from main_app.models.admin.help_model import FAQ, Contact

##--------------------------------------------- View all FAQs---------------------------------------------##

# def get_faqs_by_category_name(admin_uid, category):
#     faq_doc = FAQ.objects(admin_uid=admin_uid).first()
#     if not faq_doc:
#         return None
#     faqs = []
#     for cate in faq_doc.categories:
#         if cate["category"].strip('').lower() == category.strip('').lower():
#             return cate["faqs"]
#     return jsonify({"message" : "No FAQs"})

##---------------------------------------------- Add a new FAQ---------------------------------------------##

def add_faqs():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    category = data.get("category")
    faqs = data.get("faqs")  # List of {"question": ..., "answer": ...}

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if hasattr(exist, 'expiry_time') and exist.expiry_time:
        if datetime.datetime.now() > exist.expiry_time:
            return ({"success": False,
                     "message": "Access token has expired",
                     "token": "expired"}), 401

    if not all([admin_uid, category, isinstance(faqs, list)]) or not faqs:
        return jsonify({"error": "admin_uid, category, and a non-empty list of faqs are required"}), 400

    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        faq_doc = FAQ(admin_uid=admin_uid, categories=[])

    normalized_category = category.strip().lower()

    for cat in faq_doc.categories:
        if cat["category"].strip().lower() == normalized_category:
            cat["faqs"].extend(faqs)
            faq_doc.save()
            return jsonify({"message": f"FAQs added to {category} category"}), 201

    faq_doc.categories.append({
        "category": category,
        "faqs": faqs
    })
    faq_doc.save()

    return jsonify({"message": "FAQs added to new category"}), 201


##-----------------------------------------------Edit FAQ---------------------------------------------##
def update_faqs():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    category = data.get("category")
    updated_faqs = data.get("faqs")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if hasattr(exist, 'expiry_time') and exist.expiry_time:
        if datetime.datetime.now() > exist.expiry_time:
            return ({"success": False,
                     "message": "Access token has expired",
                     "token": "expired"}), 401

    if not all([admin_uid, category, isinstance(updated_faqs, list)]):
        return jsonify({"error": "admin_uid, category, and a list of faqs are required"}), 400

    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        return jsonify({"error": "Admin not found"}), 404

    for cat in faq_doc.categories:
        if cat["category"].lower() == category.lower():
            cat["faqs"] = updated_faqs
            faq_doc.save()
            return jsonify({"message": "FAQs updated successfully"}), 200

    return jsonify({"error": "Category not found"}), 404


def delete_faq():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")
    category = data.get("category")
    question = data.get("question")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if hasattr(exist, 'expiry_time') and exist.expiry_time:
        if datetime.datetime.now() > exist.expiry_time:
            return ({"success": False,
                     "message": "Access token has expired",
                     "token": "expired"}), 401

    if not all([admin_uid, category, question]):
        return jsonify({"error": "admin_uid, category, and question are required"}), 400

    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        return jsonify({"error": "Admin not found"}), 404

    normal_category = category.strip().lower()
    normal_question = question.strip().lower()

    for cat in faq_doc.categories:
        if cat["category"].strip().lower() == normal_category:
            original_length = len(cat["faqs"])
            cat["faqs"] = [
                faq for faq in cat["faqs"]
                if faq["question"].strip().lower() != normal_question
            ]

            if len(cat["faqs"]) == original_length:
                return jsonify({"error": "FAQ question not found"}), 404

            faq_doc.save()
            return jsonify({"message": "FAQ deleted successfully"}), 200

    return jsonify({"error": "Category not found"}), 404


##------------------------------------ View all messages sent by User---------------------------------------------##
def list_contact_messages():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    access_token = data.get("mode")
    session_id = data.get("log_alt")

    exist = Admin.objects(admin_uid=admin_uid).first()

    if not exist:
        return jsonify({"success": False, "message": "User does not exist"}), 400

    if not access_token or not session_id:
        return jsonify({"message": "Missing token or session", "success": False}), 400

    if exist.access_token != access_token:
        return ({"success": False,
                 "message": "Invalid access token"}), 401

    if exist.session_id != session_id:
        return ({"success": False,
                 "message": "Session mismatch or invalid session"}), 403

    if hasattr(exist, 'expiry_time') and exist.expiry_time:
        if datetime.datetime.now() > exist.expiry_time:
            return ({"success": False,
                     "message": "Access token has expired",
                     "token": "expired"}), 401
    messages = Contact.objects().order_by('sent_at')
    return jsonify([
        {
            "name": msg.name,
            "email": msg.email,
            "message": msg.message,
            "submitted_at": msg.date.isoformat()
        } for msg in messages
    ]), 200
