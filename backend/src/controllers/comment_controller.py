from flask import request, jsonify
from ..models.comment_model import Comment, CommentModel
from ..utils.utils import error_handler, token_required
from datetime import datetime, timedelta

@token_required
def create_comment(current_user):
    try:
        data = request.get_json()
        
        content = data.get('content')
        post_id = data.get('postId')
        user_id = data.get('userId')
        
        if not content or not post_id or not user_id:
            return error_handler(400, 'All fields are required')
        
        if user_id != current_user.id:
            return error_handler(403, 'You are not allowed to create this comment')
        
        comment_model = CommentModel(current_user._user_model.db)
        
        new_comment = Comment(
            content=content,
            post_id=post_id,
            user_id=user_id
        )
        
        saved_comment = comment_model.create_comment(new_comment)
        return jsonify(saved_comment.to_dict())
        
    except Exception as e:
        return error_handler(500, str(e))

def get_post_comments(post_id):
    try:
        from flask import current_app
        
        comment_model = CommentModel(current_app.user_model.db)
        comments = comment_model.find_by_post_id(post_id, sort_direction=-1)
        
        comments_data = [comment.to_dict() for comment in comments]
        return jsonify(comments_data)
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def like_comment(current_user, comment_id):
    try:
        comment_model = CommentModel(current_user._user_model.db)
        
        comment = comment_model.find_by_id(comment_id)
        if not comment:
            return error_handler(404, 'Comment not found')
        
        # Toggle like using the model method
        updated_comment = comment_model.toggle_like(comment_id, current_user.id)
        
        return jsonify(updated_comment.to_dict())
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def edit_comment(current_user, comment_id):
    try:
        comment_model = CommentModel(current_user._user_model.db)
        
        comment = comment_model.find_by_id(comment_id)
        if not comment:
            return error_handler(404, 'Comment not found')
        
        # Check permission
        if comment.user_id != current_user.id and not current_user.is_admin:
            return error_handler(403, 'You are not allowed to edit this comment')
        
        data = request.get_json()
        if not data.get('content'):
            return error_handler(400, 'Content is required')
        
        # Update comment
        result = comment_model.update_comment(comment_id, {'content': data['content']})
        
        if not result:
            return error_handler(404, 'Comment not found')
        
        updated_comment = comment_model.find_by_id(comment_id)
        return jsonify(updated_comment.to_dict())
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def delete_comment(current_user, comment_id):
    try:
        comment_model = CommentModel(current_user._user_model.db)
        
        comment = comment_model.find_by_id(comment_id)
        if not comment:
            return error_handler(404, 'Comment not found')
        
        # Check permission
        if comment.user_id != current_user.id and not current_user.is_admin:
            return error_handler(403, 'You are not allowed to delete this comment')
        
        # Delete comment
        result = comment_model.delete_comment(comment_id)
        
        if not result:
            return error_handler(404, 'Comment not found')
        
        return jsonify({'message': 'Comment has been deleted'})
        
    except Exception as e:
        return error_handler(500, str(e))

@token_required
def get_comments(current_user):
    if not current_user.is_admin:
        return error_handler(403, 'You are not allowed to get all comments')
    
    try:
        comment_model = CommentModel(current_user._user_model.db)
        
        start_index = int(request.args.get('startIndex', 0))
        limit = int(request.args.get('limit', 9))
        sort_direction = 1 if request.args.get('sort') == 'desc' else -1
        
        # Get comments with pagination and sorting
        comments = comment_model.get_all_comments(
            sort_direction=sort_direction,
            skip=start_index,
            limit=limit
        )
        
        comments_data = [comment.to_dict() for comment in comments]
        total_comments = comment_model.count_comments()
        
        # Last month comments count
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        last_month_comments = comment_model.count_comments({
            'created_at': {'$gte': one_month_ago}
        })
        
        return jsonify({
            'comments': comments_data,
            'totalComments': total_comments,
            'lastMonthComments': last_month_comments
        })
        
    except Exception as e:
        return error_handler(500, str(e))