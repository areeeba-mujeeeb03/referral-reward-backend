from mongoengine import StringField, IntField, Document

class DiscountCoupons(Document):
    admin_uid = StringField()
    product_id = StringField()
    discount_code = StringField()
