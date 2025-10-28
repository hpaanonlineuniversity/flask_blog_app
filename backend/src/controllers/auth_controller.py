from flask import request, jsonify, make_response
from ..models.user_model import User, bcrypt
from ..utils.utils import error_handler, generate_token

def signup(user_model):
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return error_handler(400, 'All fields are required')
    
    # Check if user already exists
    if user_model.find_by_email(email):
        return error_handler(400, 'Email already exists')
    
    if user_model.find_by_username(username):
        return error_handler(400, 'Username already exists')
    
    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    # Create new user
    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )
    
    try:
        user_model.create_user(new_user)
        return jsonify({
            'success': True,
            'message': 'Signup successful'
        })
    except Exception as e:
        return error_handler(500, str(e))

def signin(user_model):
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return error_handler(400, 'All fields are required')
    
    try:
        valid_user = user_model.find_by_email(email)
        if not valid_user:
            return error_handler(404, 'User not found')
        
        if not bcrypt.check_password_hash(valid_user.password, password):
            return error_handler(400, 'Invalid password')
        
        token = generate_token(valid_user._id, valid_user.is_admin)
        
        user_data = valid_user.to_dict()
        
        
       ## response = make_response(jsonify({
        ##    'success': True,
         ##   'user': user_data
        ##}))

        response_data = {
            'success': True
        }
        response_data.update(user_data)

        response = make_response(jsonify(response_data))
        
        response.set_cookie(
            'access_token',
            token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return error_handler(500, str(e))

def google_auth(user_model):
    data = request.get_json()
    
    email = data.get('email')
    name = data.get('name')
    google_photo_url = data.get('googlePhotoUrl')
    
    try:
        user = user_model.find_by_email(email)
        
        if user:
            token = generate_token(user._id, user.is_admin)
            user_data = user.to_dict()
            
            ##response = make_response(jsonify({
            ##    'success': True,
            ##    'user': user_data
            ##}))

            response_data = {
                'success': True
            }
            response_data.update(user_data)

            response = make_response(jsonify(response_data))
            
            response.set_cookie(
                'access_token',
                token,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            
            return response
        else:
            # Generate random password for Google users
            import random
            import string
            
            generated_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            hashed_password = bcrypt.generate_password_hash(generated_password).decode('utf-8')
            
            # Generate username from name
            base_username = name.lower().replace(' ', '')
            username = f"{base_username}{random.randint(1000, 9999)}"
            
            # Ensure username is unique
            while user_model.find_by_username(username):
                username = f"{base_username}{random.randint(1000, 9999)}"
            
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                profile_picture=google_photo_url
            )
            
            user_model.create_user(new_user)
            
            token = generate_token(new_user._id, new_user.is_admin)
            user_data = new_user.to_dict()
            
            ##response = make_response(jsonify({
            ##    'success': True,
            ##    'user': user_data
            ##}))

            response_data = {
                'success': True
            }
            response_data.update(user_data)

            response = make_response(jsonify(response_data))
            
            response.set_cookie(
                'access_token',
                token,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            
            return response
            
    except Exception as e:
        return error_handler(500, str(e))

def signout():
    response = make_response(jsonify({
        'success': True,
        'message': 'Signed out successfully'
    }))
    
    response.set_cookie('access_token', '', expires=0)
    return response