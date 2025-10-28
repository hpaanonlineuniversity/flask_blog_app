from flask import Blueprint
from ..controllers.comment_controller import (
    create_comment, get_post_comments, like_comment, 
    edit_comment, delete_comment, get_comments
)

def create_comment_blueprint():
    comment_bp = Blueprint('comment', __name__)
    
    @comment_bp.route('/create', methods=['POST'])
    def create_comment_route():
        return create_comment()
    
    @comment_bp.route('/getPostComments/<string:post_id>', methods=['GET'])
    def get_post_comments_route(post_id):
        return get_post_comments(post_id)
    
    @comment_bp.route('/likeComment/<string:comment_id>', methods=['PUT'])
    def like_comment_route(comment_id):
        return like_comment(comment_id)
    
    @comment_bp.route('/editComment/<string:comment_id>', methods=['PUT'])
    def edit_comment_route(comment_id):
        return edit_comment(comment_id)
    
    @comment_bp.route('/deleteComment/<string:comment_id>', methods=['DELETE'])
    def delete_comment_route(comment_id):
        return delete_comment(comment_id)
    
    @comment_bp.route('/getcomments', methods=['GET'])
    def get_comments_route():
        return get_comments()
    
    return comment_bp