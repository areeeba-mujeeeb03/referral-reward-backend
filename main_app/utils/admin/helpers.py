import random
import datetime
from cryptography.fernet import Fernet

# FERNET_SECRET_KEY = 'awpo[oiufttttttttttttttttttttcfbbbbgggggxb'
# fernet = Fernet(FERNET_SECRET_KEY)

from main_app.models.admin.product_model import Product
# from main_app.models.admin.product_offer_model import Offer


def generate_otp(length=6):
    return ''.join(random.choices("0123456789", k=length))

def get_expiry_time(minutes=5):
    return datetime.datetime.now() + datetime.timedelta(minutes=minutes)


# def encrypt_admin_uid(admin_uid: str) -> str:
#     return fernet.encrypt(admin_uid.encode()).decode()
#
# def decrypt_admin_uid(encrypted_uid: str) -> str:
#     return fernet.decrypt(encrypted_uid.encode()).decode()
# -----------------------------------------------------------------------------------------

# Generate product uid

#  Example PROD_01, PROD_02, ....

def generate_product_uid():
    count = Product.objects.count() + 1
    return f"PROD_{str(count).zfill(2)}"  

# --------------------------------------------------------------------------------------------

#  Genrate offer uid 

# Example OFR_01, OFR_02, .....

# def generate_offer_uid():
#     count = Offer.objects.count() + 1
#     return f"OFR_{str(count).zfill(2)}"


