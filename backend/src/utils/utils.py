from flask import jsonify
import functools

def error_handler(status_code, message):
    response = jsonify({
        'success': False,
        'error': {
            'status': status_code,
            'message': message
        }
    })
    response.status_code = status_code
    return response

def generate_token(user_id, is_admin=False):
    import jwt
    from datetime import datetime, timedelta
    from flask import current_app
    
    payload = {
        'id': str(user_id),
        'isAdmin': is_admin,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    
    token = jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    return token

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, current_app
        import jwt
        from bson import ObjectId
        
        token = request.cookies.get('access_token')
        
        if not token:
            return error_handler(401, 'Token is missing')
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            current_user = current_app.user_model.find_by_id(data['id'])
            if not current_user:
                return error_handler(401, 'Invalid token')
        except jwt.ExpiredSignatureError:
            return error_handler(401, 'Token has expired')
        except jwt.InvalidTokenError:
            return error_handler(401, 'Invalid token')
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return error_handler(403, 'Admin access required')
        return f(current_user, *args, **kwargs)
    return decorated

def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, current_app
        import jwt
        from bson import ObjectId
        
        token = request.cookies.get('access_token')
        
        if not token:
            return error_handler(401, 'Token is missing')
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            current_user = current_app.user_model.find_by_id(data['id'])
            if not current_user:
                return error_handler(401, 'Invalid token')
            
            # Add user_model reference to current_user for database operations
            current_user._user_model = current_app.user_model
            
        except jwt.ExpiredSignatureError:
            return error_handler(401, 'Token has expired')
        except jwt.InvalidTokenError:
            return error_handler(401, 'Invalid token')
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Update the token_required decorator to include post_model
def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, current_app
        import jwt
        from bson import ObjectId
        
        token = request.cookies.get('access_token')
        
        if not token:
            return error_handler(401, 'Token is missing')
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            current_user = current_app.user_model.find_by_id(data['id'])
            if not current_user:
                return error_handler(401, 'Invalid token')
            
            # Add model references to current_user for database operations
            current_user._user_model = current_app.user_model
            current_user._post_model = current_app.post_model  # ADD THIS
            
        except jwt.ExpiredSignatureError:
            return error_handler(401, 'Token has expired')
        except jwt.InvalidTokenError:
            return error_handler(401, 'Invalid token')
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Update the token_required decorator to include all models
def token_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        from flask import request, current_app
        import jwt
        from bson import ObjectId
        
        token = request.cookies.get('access_token')
        
        if not token:
            return error_handler(401, 'Token is missing')
        
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            current_user = current_app.user_model.find_by_id(data['id'])
            if not current_user:
                return error_handler(401, 'Invalid token')
            
            # Add model references to current_user for database operations
            current_user._user_model = current_app.user_model
            current_user._post_model = current_app.post_model
            current_user._comment_model = current_app.comment_model  # ADD THIS
            
        except jwt.ExpiredSignatureError:
            return error_handler(401, 'Token has expired')
        except jwt.InvalidTokenError:
            return error_handler(401, 'Invalid token')
        
        return f(current_user, *args, **kwargs)
    
    return decorated