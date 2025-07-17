from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, ListField, EmbeddedDocumentField, \
    IntField, FloatField


class DiscountCoupon(EmbeddedDocument):
    product_id = StringField(required=True)
    coupon_code = StringField(required=True, unique=True)
    original_amt = FloatField()
    discount_amt = FloatField()
    off_percent = IntField()
    description = StringField()
    validity_till = StringField()

class ProductDiscounts(Document):
    admin_uid = StringField(required=True)
    coupons = ListField(EmbeddedDocumentField(DiscountCoupon))

    meta = {"db_alias" : "admin-db", "collection" : "DiscountCoupons"}

