from flask import request, jsonify
from main_app.models.admin.help_model import FAQ, Contact



##--------------------------------------------- View all FAQs---------------------------------------------##

def list_faqs():
    faqs = FAQ.objects()
    return jsonify([
        {"id": str(faq.id), "question": faq.question, "answer": faq.answer}
        for faq in faqs
    ]), 200

##---------------------------------------------- Add a new FAQ---------------------------------------------##

def add_faq():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")
    category = data.get("category")

    if not question or not answer:
        return jsonify({"error": "Both question and answer are required"}), 400

    faq = FAQ(question=question, answer=answer, category = category)
    faq.save()
    return jsonify({"message": "FAQ added successfully"}), 201

##-----------------------------------------------Edit FAQ---------------------------------------------##
def update_faq(faq_id):
    data = request.get_json()
    faq = FAQ.objects(id=faq_id).first()

    if not faq:
        return jsonify({"error": "FAQ not found"}), 404

    faq.update(
        question=data.get("question", faq.question),
        answer=data.get("answer", faq.answer)
    )
    return jsonify({"message": "FAQ updated"}), 200

# Delete FAQ
def delete_faq(faq_id):
    faq = FAQ.objects(id=faq_id).first()
    if not faq:
        return jsonify({"error": "FAQ not found"}), 404

    faq.delete()
    return jsonify({"message": "FAQ deleted"}), 200

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
