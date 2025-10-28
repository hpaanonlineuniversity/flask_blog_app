from flask import Flask
from pymongo import MongoClient
from .models.user_model import UserModel
from .models.post_model import PostModel
from .models.comment_model import CommentModel
from .routes.auth_routes import create_auth_blueprint
from .routes.user_routes import create_user_blueprint
from .routes.post_routes import create_post_blueprint
from .routes.comment_routes import create_comment_blueprint
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
    post_model = PostModel(db)
    comment_model = CommentModel(db)

    user_model.create_indexes()
    post_model.create_indexes()
    comment_model.create_indexes()
    
    # Store user_model in app context for easy access
    app.user_model = user_model
    app.post_model = post_model
    app.comment_model = comment_model

    # Register Blueprints
    auth_bp = create_auth_blueprint(user_model)
    user_bp = create_user_blueprint(user_model)
    post_bp = create_post_blueprint()
    comment_bp = create_comment_blueprint()
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user') 
    app.register_blueprint(post_bp, url_prefix='/api/post')
    app.register_blueprint(comment_bp, url_prefix='/api/comment')
    
    # CORS setup
    from flask_cors import CORS
    CORS(app, supports_credentials=True)
    
    return app