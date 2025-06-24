from flask import request

def handle_admin_login():
    data = request.json()
    return