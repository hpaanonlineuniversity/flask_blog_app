from flask import current_app
from flask_bcrypt import Bcrypt
from datetime import datetime
import jwt
import os

bcrypt = Bcrypt()

class User:
    def __init__(self, username, email, password, profile_picture=None, is_admin=False, _id=None, created_at=None, updated_at=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.profile_picture = profile_picture or 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png'
        self.is_admin = is_admin
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': str(self._id),
            'username': self.username,
            'email': self.email,
            'profilePicture': self.profile_picture,
            'isAdmin': self.is_admin,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at
        }
    
    @staticmethod
    def from_dict(data):
        return User(
            _id=data.get('_id'),
            username=data['username'],
            email=data['email'],
            password=data['password'],
            profile_picture=data.get('profile_picture'),
            is_admin=data.get('is_admin', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

class UserModel:
    def __init__(self, db):
        self.db = db
        self.collection = db.users
    
    def create_indexes(self):
        self.collection.create_index([('username', 1)], unique=True)
        self.collection.create_index([('email', 1)], unique=True)
    
    def find_by_email(self, email):
        user_data = self.collection.find_one({'email': email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def find_by_username(self, username):
        user_data = self.collection.find_one({'username': username})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def find_by_id(self, user_id):
        from bson import ObjectId
        user_data = self.collection.find_one({'_id': ObjectId(user_id)})
        if user_data:
            return User.from_dict(user_data)
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
        return user
    
    def update_user(self, user_id, update_data):
        from bson import ObjectId
        update_data['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )