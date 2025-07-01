import bcrypt
import random
import string
import uuid
import datetime
from flask import session

##-------------------------------------TAG_ID AND USER_ID-----------------------------------------------##
def generate_tag_id(username, mobile_number):
    mobile_str = str(mobile_number)
    name_part = username[:3].upper()
    mobile_part = mobile_str[-4:]
    random_part = ''.join(random.choices(string.digits, k=3))
    tag_id = f"{name_part}{mobile_part}{random_part}"
    return tag_id

def hash_tag_id(username, mobile_number):
    tag_id = generate_tag_id(username, mobile_number)
    byte_tag_id = tag_id.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_tag_id = bcrypt.hashpw(byte_tag_id, salt)
    return hashed_tag_id.decode('utf-8'), tag_id

def verify_tag_id(tag_id: str, hashed: str) -> bool:
    return bcrypt.checkpw(tag_id.encode('utf-8'), hashed.encode('utf-8'))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(input_password, stored_hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_hashed_password.encode('utf-8'))

##---------------------------------GENERATION OF INVITATION LINK---------------------------------------##
def generate_invite_link(hashed_tag_id):
    return f"https://wealthelite.com/invite-link/{hashed_tag_id}"

##---------------------------CREATE SESSION AND TOKEN FOR USER WITH EXPIRY----------------------------------##

def create_user_session(user_id):
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    session['user_id'] = user_id

    session_data = {
        "session_id": session_id,
        "created_at": datetime.datetime.now()
    }
    return session_id

def generate_access_token(user_id):
    access_token = f"k{datetime.datetime.now()}_ITuid_{user_id}"
    return access_token

def insert_dict(col_name, data):
    col_name.insert_one(data)

def update(user_id,col_name, data):
    find = col_name.find_one({"user_id" : user_id})
    find.update_one(data)