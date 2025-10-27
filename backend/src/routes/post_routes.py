from flask import Blueprint
from ..controllers.post_controller import create_post, get_posts, delete_post, update_post

def create_post_blueprint():
    post_bp = Blueprint('post', __name__)
    
    @post_bp.route('/create', methods=['POST'])
    def create_post_route():
        return create_post()
    
    @post_bp.route('/getposts', methods=['GET'])
    def get_posts_route():
        return get_posts()
    
    @post_bp.route('/deletepost/<string:post_id>/<string:user_id>', methods=['DELETE'])
    def delete_post_route(post_id, user_id):
        return delete_post(post_id, user_id)
    
    @post_bp.route('/updatepost/<string:post_id>/<string:user_id>', methods=['PUT'])
    def update_post_route(post_id, user_id):
        return update_post(post_id, user_id)
    
    return post_bp