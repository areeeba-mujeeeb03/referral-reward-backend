import random
import datetime 
from main_app.models.admin.product_model import Product
from main_app.models.admin.product_offer_model import Offer


def generate_otp(length=6):
    return ''.join(random.choices("0123456789", k=length))

def get_expiry_time(minutes=5):
    return datetime.datetime.now() + datetime.timedelta(minutes=minutes)

# -----------------------------------------------------------------------------------------

# Generate product uid

#  Example PROD_01, PROD_02, ....

def generate_product_uid():
    count = Product.objects.count() + 1
    return f"PROD_{str(count).zfill(2)}"  

# --------------------------------------------------------------------------------------------

#  Genrate offer uid 

# Example OFR_01, OFR_02, .....

def generate_offer_uid():
    count = Offer.objects.count() + 1
    return f"OFR_{str(count).zfill(2)}"


