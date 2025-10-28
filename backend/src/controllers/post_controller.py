from flask import request, jsonify
from ..models.post_model import Post, PostModel
from ..utils.utils import error_handler, token_required
from datetime import datetime, timedelta
import re

@token_required
def create_post(current_user):
    if not current_user.is_admin:
        return error_handler(403, 'You are not allowed to create a post')
    
    data = request.get_json()
    
    if not data.get('title') or not data.get('content'):
        return error_handler(400, 'Please provide all required fields')
    
    # Generate slug from title
    slug = data['title'].split(' ')
    slug = '-'.join(slug).lower()
    slug = re.sub(r'[^a-zA-Z0-9-]', '', slug)
    
    # Check if slug already exists and make it unique
    post_model = current_user._user_model.db.posts  # Access posts collection
    existing_post = post_model.find_one({'slug': slug})
    if existing_post:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
    
    try:
        new_post = Post(
            user_id=current_user.id,
            content=data['content'],
            title=data['title'],
            slug=slug,
            image=data.get('image'),
            category=data.get('category')
        )
        
        # Create PostModel instance and save
        post_model_obj = PostModel(current_user._user_model.db)
        saved_post = post_model_obj.create_post(new_post)
        
        return jsonify(saved_post.to_dict()), 201
        
    except Exception as e:
        if 'duplicate key error' in str(e):
            return error_handler(400, 'Post with this title or slug already exists')
        return error_handler(500, str(e))

def get_posts():
    try:
        from flask import current_app
        from ..models.user_model import UserModel

        # Get database from UserModel instance
        user_model = UserModel()
        post_model = PostModel(user_model.db)  # Use user_model.db instead
        
        # Get query parameters
        start_index = int(request.args.get('startIndex', 0))
        limit = int(request.args.get('limit', 9))
        sort_direction = 1 if request.args.get('order') == 'asc' else -1
        
        user_id = request.args.get('userId')
        category = request.args.get('category')
        slug = request.args.get('slug')
        post_id = request.args.get('postId')
        search_term = request.args.get('searchTerm')
        
        # Build query filter
        query_filter = {}
        
        if user_id:
            query_filter['user_id'] = user_id
        if category:
            query_filter['category'] = category
        if slug:
            query_filter['slug'] = slug
        if post_id:
            from bson import ObjectId
            try:
                query_filter['_id'] = ObjectId(post_id)
            except:
                return error_handler(400, 'Invalid post ID')
        
        if search_term:
            query_filter['$or'] = [
                {'title': {'$regex': search_term, '$options': 'i'}},
                {'content': {'$regex': search_term, '$options': 'i'}}
            ]
        
        # Get posts
        post_model = PostModel(current_app.user_model.db)
        posts = post_model.search_posts(
            query_filter=query_filter,
            sort_field='updated_at',
            sort_direction=sort_direction,
            skip=start_index,
            limit=limit
        )
        
        posts_data = [post.to_dict() for post in posts]
        total_posts = post_model.count_posts()
        
        # Last month posts count
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        last_month_posts = post_model.count_posts({
            'created_at': {'$gte': one_month_ago}
        })
        
        return jsonify({
            'posts': posts_data,
            'totalPosts': total_posts,
            'lastMonthPosts': last_month_posts
        })
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def delete_post(current_user, post_id, user_id):
    if not current_user.is_admin or current_user.id != user_id:
        return error_handler(403, 'You are not allowed to delete this post')
    
    try:
        post_model = PostModel(current_user._user_model.db)
        result = post_model.delete_post(post_id)
        
        if not result:
            return error_handler(404, 'Post not found')
        
        return jsonify({'message': 'The post has been deleted'})
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def update_post(current_user, post_id, user_id):
    if not current_user.is_admin or current_user.id != user_id:
        return error_handler(403, 'You are not allowed to update this post')
    
    try:
        data = request.get_json()
        
        update_data = {}
        if 'title' in data:
            update_data['title'] = data['title']
        if 'content' in data:
            update_data['content'] = data['content']
        if 'category' in data:
            update_data['category'] = data['category']
        if 'image' in data:
            update_data['image'] = data['image']
        
        post_model = PostModel(current_user._user_model.db)
        result = post_model.update_post(post_id, update_data)
        
        if not result:
            return error_handler(404, 'Post not found')
        
        updated_post = post_model.find_by_id(post_id)
        return jsonify(updated_post.to_dict())
        
    except Exception as e:
        return error_handler(500, str(e))