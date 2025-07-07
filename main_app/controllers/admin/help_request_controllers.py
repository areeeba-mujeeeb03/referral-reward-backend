from flask import request, jsonify
from main_app.models.admin.help_model import FAQ, Contact

##--------------------------------------------- View all FAQs---------------------------------------------##

def get_faqs_by_category_name(admin_uid, category):
    if not category:
        return None

    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        return None

    for cat in faq_doc.categories:
        if cat["category"].strip(" ,").lower() == category.strip(" ,").lower():
            return cat["faqs"]
    return None

##---------------------------------------------- Add a new FAQ---------------------------------------------##

def add_faq():
    data = request.get_json()
    admin_uid = data.get("admin_uid")
    category = data.get("category")
    question = data.get("question")
    answer = data.get("answer")

    if not all([admin_uid, category, question, answer]):
        return jsonify({"error": "All fields are required"}), 400

    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        faq_doc = FAQ(admin_uid=admin_uid, categories=[])

    # Check if category exists
    for cat in faq_doc.categories:
        if cat["category"].lower() == category.lower():
            cat["faqs"].append({"question": question, "answer": answer})
            break
    else:
        faq_doc.categories.append({
            "category": category,
            "faqs": [{"question": question, "answer": answer}]
        })

    faq_doc.save()
    return jsonify({"message": "FAQ added successfully"}), 201

##-----------------------------------------------Edit FAQ---------------------------------------------##
def update_faq(admin_uid, category, index):
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")

    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        return jsonify({"error": "Admin not found"}), 404

    for category in faq_doc.categories:
        if category["category"].lower() == category.lower():
            if 0 <= index < len(category["faqs"]):
                if question:
                    category["faqs"][index]["question"] = question
                if answer:
                    category["faqs"][index]["answer"] = answer
                faq_doc.save()
                return jsonify({"message": "FAQ updated"}), 200
            else:
                return jsonify({"error": "FAQ index out of range"}), 400

    return jsonify({"error": "Category not found"}), 404


def delete_faq(admin_uid, category, index):
    faq_doc = FAQ.objects(admin_uid=admin_uid).first()
    if not faq_doc:
        return jsonify({"error": "Admin not found"}), 404

    for cat in faq_doc.categories:
        if cat["category"].lower() == category.lower():
            if 0 <= index < len(cat["faqs"]):
                cat["faqs"].pop(index)
                faq_doc.save()
                return jsonify({"message": "FAQ deleted"}), 200
            else:
                return jsonify({"error": "FAQ index out of range"}), 400

    return jsonify({"error": "Category not found"}), 404

##------------------------------------ View all messages sent by User---------------------------------------------##
def list_contact_messages():
    messages = Contact.objects().order_by('sent_at')
    return jsonify([
        {
            "name": msg.username,
            "email": msg.email,
            "message": msg.message,
            "submitted_at": msg.date.isoformat()
        } for msg in messages
    ]), 200
