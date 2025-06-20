import os
from flask import Flask
from mongoengine import connect
# Import user routes and admin routes 
from main_app.routes.user.user_routes import user_bp
# from main_app.routes.admin import admin_routes


app = Flask(__name__)



# Secret key for session management (CSRF, etc.)
app.config["SECRET_KEY"] = "areeba-mujeeb-is-Smart"

# Connect to MongoDB using mongoengine
connect(db="LoyaltyProgram", host="localhost", port=27017)

# User Routes
app.register_blueprint(user_bp)

# Admin Routes
# app.register_blueprint(admin_routes)

if __name__ == "__main__":
    app.run(port=5000, debug =True)