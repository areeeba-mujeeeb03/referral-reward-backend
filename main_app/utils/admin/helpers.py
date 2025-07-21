import random
import datetime
from cryptography.fernet import Fernet

# FERNET_SECRET_KEY = 'awpo[oiufttttttttttttttttttttcfbbbbgggggxb'
# fernet = Fernet(FERNET_SECRET_KEY)

from main_app.models.admin.product_model import Product
from main_app.models.admin.product_offer_model import Offer
from main_app.models.admin.prize_model import PrizeDetail, AdminPrizes

def generate_otp(length=6):
    return ''.join(random.choices("0123456789", k=length))

def get_expiry_time(minute = 1):
    return datetime.datetime.now() + datetime.timedelta(minute)


# def encrypt_admin_uid(admin_uid: str) -> str:
#     return fernet.encrypt(admin_uid.encode()).decode()
#
# def decrypt_admin_uid(encrypted_uid: str) -> str:
#     return fernet.decrypt(encrypted_uid.encode()).decode()
# -----------------------------------------------------------------------------------------

# Generate product uid

#  Example PROD_01, PROD_02, ....

# def generate_product_uid():
#     count = Product.objects.count() + 1
#     return f"PROD_{str(count).zfill(2)}"  

def generate_product_uid(admin_uid):
    prod_doc = Product.objects(admin_uid=admin_uid).first()
    count = 1
    if prod_doc:
        for product in prod_doc.products:
            if product:
                  count = len(prod_doc.products) + 1
    else:
        count = 1
    return f"PROD_{str(count).zfill(2)}"  

# --------------------------------------------------------------------------------------------

# --------------------------------  Generate offer uid ------------------------------------------#

# Example OFR_01, OFR_02, .....

# def generate_offer_uid(admin_uid):
#     count = Offer.objects(admin_uid=admin_uid).count() + 1
#     return f"OFR_{str(count).zfill(2)}"
  

def generate_offer_uid(admin_uid):
    offer_doc = Offer.objects(admin_uid=admin_uid).first()
    count = 1
    if offer_doc:
        for offer in offer_doc.offers:
            if offer:
                count = len(offer_doc.offers) + 1
    else:
        count = 1
    return f"OFR_{str(count).zfill(2)}"

# ---------------------------------------------------------------------------------------

# ---------------------------------Exclusive perks ----------------------------------------#

def generate_prize_uid(admin_uid):
    # new_prize = PrizeDetail.object(admin_uid=admin_uid).first()
    # count = 1
    # if new_prize:
    #     for prize in new_prize.prizes:
    #         if prize:
    #             count = len(new_prize.prizes) + 1
    # else:
    #     count = 1        
      admin_prizes = AdminPrizes.objects(admin_uid=admin_uid).first()
    
      if admin_prizes and admin_prizes.prizes:
        count = len(admin_prizes.prizes) + 1
      else:
        count = 1    
      return f"PRZ_{str(count).zfill(2)}"
