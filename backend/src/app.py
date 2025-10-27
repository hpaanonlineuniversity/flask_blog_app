from flask import Flask
from pymongo import MongoClient
from .models.user_model import UserModel
from .routes.auth_routes import create_auth_blueprint
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'your-secret-key-here')
    
    app.config["MONGO_URI"] = "mongodb://admin:password@mongodb:27017/newuserdb?authSource=admin"
    
    # Initialize MongoDB
    client = MongoClient(app.config['MONGO_URI'])
    db = client.get_database()
    
    # Initialize User Model
    user_model = UserModel(db)
    user_model.create_indexes()
    
    # Store user_model in app context for easy access
    app.user_model = user_model
    
    # Register Blueprints
    auth_bp = create_auth_blueprint(user_model)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # CORS setup (if needed)
    from flask_cors import CORS
    CORS(app, supports_credentials=True)
    
    return app