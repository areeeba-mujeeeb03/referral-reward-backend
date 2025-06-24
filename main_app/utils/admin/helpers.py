import random
import datetime

def generate_otp(length=6):
    return ''.join(random.choices("0123456789", k=length))

def get_expiry_time(minutes=5):
    return datetime.datetime.now() + datetime.timedelta(minutes=minutes)
