import os
from flask import Flask
from mongoengine import connect
from main_app.routes.user.user_routes import user_bp
from main_app.routes.admin.admin_routes import admin_bp
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# Secret key for session management (CSRF, etc.)
app.config["SECRET_KEY"] = "areeba-mujeeb-is-Smart"

# Connect to MongoDB using mongoengine
#user's DB
connect(db="LoyaltyProgram-user", alias="default", host="localhost", port=27017)
#admin's DB
connect(db="LoyaltyProgram-admin", alias="admin-db", host="localhost", port=27017)

# User Routes
app.register_blueprint(user_bp)

# Admin Routes
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(port=5000, debug =True)