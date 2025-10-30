from flask import current_app
from flask_bcrypt import Bcrypt
from datetime import datetime
import jwt
import os
from bson import ObjectId

bcrypt = Bcrypt()

class User:
    def __init__(self, username, email, password, profile_picture=None, is_admin=False, _id=None, created_at=None, updated_at=None, user_model=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.profile_picture = profile_picture or 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self._user_model = user_model  # Reference to UserModel for database operations
    
    @property
    def id(self):
        return str(self._id) if self._id else None
    
    def to_dict(self):
        return {
            '_id': self.id,
            'username': self.username,
            'email': self.email,
            'profilePicture': self.profile_picture,
            'isAdmin': self.is_admin,
            'createdAt': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updatedAt': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }
    
    @staticmethod
    def from_dict(data, user_model=None):
        return User(
            _id=data.get('_id'),
            username=data['username'],
            email=data['email'],
            password=data['password'],
            profile_picture=data.get('profile_picture'),
            is_admin=data.get('is_admin', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            user_model=user_model
        )

class UserModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
    
    def _to_object_id(self, id_str):
        """Convert string ID to ObjectId"""
        try:
            return ObjectId(id_str)
        except:
            return None
    
    def create_indexes(self):
        self.collection.create_index([('username', 1)], unique=True)
        self.collection.create_index([('email', 1)], unique=True)
        self.collection.create_index([('created_at', -1)])
    
    def find_by_email(self, email):
        user_data = self.collection.find_one({'email': email})
        if user_data:
            return User.from_dict(user_data, self)
        return None
    
    def find_by_username(self, username):
        user_data = self.collection.find_one({'username': username})
        if user_data:
            return User.from_dict(user_data, self)
        return None
    
    def find_by_id(self, user_id):
        object_id = self._to_object_id(user_id)
        if not object_id:
            return None
        user_data = self.collection.find_one({'_id': object_id})
        if user_data:
            return User.from_dict(user_data, self)
        return None
    
    def create_user(self, user):
        user_data = {
            'username': user.username,
            'email': user.email,
            'password': user.password,
            'profile_picture': user.profile_picture,
            'is_admin': user.is_admin,
            'created_at': user.created_at,
            'updated_at': user.updated_at
        }
        
        result = self.collection.insert_one(user_data)
        user._id = result.inserted_id
        user._user_model = self
        return user
    
    def update_user(self, user_id, update_data):
        object_id = self._to_object_id(user_id)
        if not object_id:
            raise ValueError("Invalid user ID")
        
        update_data['updated_at'] = datetime.utcnow()
        result = self.collection.update_one(
            {'_id': object_id},
            {'$set': update_data}
        )
        return result.modified_count > 0
    
    def delete_user(self, user_id):
        object_id = self._to_object_id(user_id)
        if not object_id:
            raise ValueError("Invalid user ID")
        
        result = self.collection.delete_one({'_id': object_id})
        return result.deleted_count > 0
    

    def create_default_admin(self):
        """Environment variables ကနေ admin details ယူပြီး ဖန်တီးခြင်း"""
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        existing_admin = self.find_by_email(admin_email)
        if existing_admin:
            print("Admin user already exists")
            return existing_admin
        
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        
        admin_user = User(
            username=admin_username,
            email=admin_email,
            password=hashed_password,
            is_admin=True
        )
        
        try:
            created_admin = self.create_user(admin_user)
            print("Default admin user created successfully!")
            return created_admin
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")
            return None
