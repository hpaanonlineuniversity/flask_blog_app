from flask import request, jsonify, make_response
from ..models.user_model import User, UserModel
from ..utils.utils import error_handler, token_required
import bcrypt
from datetime import datetime, timedelta

def test():
    return jsonify({'message': 'API is working!'})

@token_required
def update_user(current_user, user_id):
    print(f"Current User ID: {current_user.id}")
    print(f"Target User ID: {user_id}")
    
    # Check if user is updating their own profile
    if current_user.id != user_id:
        return error_handler(403, 'You are not allowed to update this user')
    
    data = request.get_json()
    
    # Password validation and hashing
    if 'password' in data and data['password']:
        if len(data['password']) < 6:
            return error_handler(400, 'Password must be at least 6 characters')
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Username validation
    if 'username' in data and data['username']:
        username = data['username']
        if len(username) < 6 or len(username) > 40:
            return error_handler(400, 'Username must be between 6 and 20 characters')
        if ' ' in username:
            return error_handler(400, 'Username cannot contain spaces')
        if username != username.lower():
            return error_handler(400, 'Username must be lowercase')
        if not username.isalnum():
            return error_handler(400, 'Username can only contain letters and numbers')
    
    try:
        # Get user_model from app context
        user_model = current_user._user_model
        
        update_data = {}
        if 'username' in data:
            update_data['username'] = data['username']
        if 'email' in data:
            update_data['email'] = data['email']
        if 'profilePicture' in data:
            update_data['profile_picture'] = data['profilePicture']
        if 'password' in data and data['password']:
            update_data['password'] = data['password']
        
        user_model.update_user(user_id, update_data)
        updated_user = user_model.find_by_id(user_id)
        
        user_data = updated_user.to_dict()
        return jsonify(user_data)
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def delete_user(current_user, user_id):
    if not current_user.is_admin and current_user.id != user_id:
        return error_handler(403, 'You are not allowed to delete this user')
    
    try:
        user_model = current_user._user_model
        user_model.collection.delete_one({'_id': user_model._to_object_id(user_id)})
        return jsonify({'message': 'User has been deleted'})
    except Exception as e:
        return error_handler(500, str(e))

def signout():
    response = make_response(jsonify({'message': 'User has been signed out'}))
    response.set_cookie('access_token', '', expires=0)
    return response

@token_required
def get_users(current_user):
    if not current_user.is_admin:
        return error_handler(403, 'You are not allowed to see all users')
    
    try:
        user_model = current_user._user_model
        
        start_index = int(request.args.get('startIndex', 0))
        limit = int(request.args.get('limit', 9))
        sort_direction = 1 if request.args.get('sort') == 'asc' else -1
        
        # Get users with pagination and sorting
        users_cursor = user_model.collection.find().sort('created_at', sort_direction).skip(start_index).limit(limit)
        users = [User.from_dict(user) for user in users_cursor]
        
        users_without_password = [user.to_dict() for user in users]
        
        total_users = user_model.collection.count_documents({})
        
        # Last month users count
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        last_month_users = user_model.collection.count_documents({
            'created_at': {'$gte': one_month_ago}
        })
        
        return jsonify({
            'users': users_without_password,
            'totalUsers': total_users,
            'lastMonthUsers': last_month_users
        })
        
    except Exception as e:
        return error_handler(500, str(e))

def get_user(user_id):
    try:
        from flask import current_app
        user_model = current_app.user_model
        user = user_model.find_by_id(user_id)
        
        if not user:
            return error_handler(404, 'User not found')
        
        user_data = user.to_dict()
        return jsonify(user_data)
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def update_user_admin(current_user, user_id):
    try:
        # Check if user is authenticated and is admin
        if not current_user.is_admin:
            return error_handler(403, 'You are not allowed to update admin status')
        
        # Prevent self-admin-status change
        if current_user.id == user_id:
            return error_handler(403, 'You cannot change your own admin status')
        
        data = request.get_json()
        if 'isAdmin' not in data:
            return error_handler(400, 'isAdmin field is required')
        
        user_model = current_user._user_model
        user_model.update_user(user_id, {'is_admin': data['isAdmin']})
        
        updated_user = user_model.find_by_id(user_id)
        user_data = updated_user.to_dict()
        
        return jsonify(user_data)
        
    except Exception as e:
        return error_handler(500, str(e))