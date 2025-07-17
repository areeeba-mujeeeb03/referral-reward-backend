from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, ListField, EmbeddedDocumentField, \
    IntField


class DiscountCoupon(EmbeddedDocument):
    title = StringField(required=True)
    product_id = StringField(required=True)
    coupon_code = StringField(required=True, unique=True)
    original_amt = StringField()
    discounted_amt = StringField()
    off_percent = IntField()
    description = StringField()
    image = StringField()
    start_date = DateTimeField()
    end_date = DateTimeField()

class ProductDiscounts(Document):
    admin_uid = StringField(required=True)
    coupons = ListField(EmbeddedDocumentField(DiscountCoupon))

    meta = {"db_alias" : "admin-db", "collection" : "DiscountCoupons"}

