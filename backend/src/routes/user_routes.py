from flask import Blueprint
from ..controllers.user_controller import (
    test, update_user, delete_user, signout, 
    get_users, get_user, update_user_admin
)

def create_user_blueprint(user_model):
    user_bp = Blueprint('user', __name__)
    
    # Store user_model in blueprint for access in controllers
    user_bp.user_model = user_model
    
    @user_bp.route('/test', methods=['GET'])
    def test_route():
        return test()
    
    @user_bp.route('/update/<string:user_id>', methods=['PUT', 'POST'])
    def update_user_route(user_id):
        return update_user(user_id)
    
    @user_bp.route('/delete/<string:user_id>', methods=['DELETE'])
    def delete_user_route(user_id):
        return delete_user(user_id)
    
    @user_bp.route('/signout', methods=['GET'])
    def signout_route():
        return signout()
    
    @user_bp.route('/getusers', methods=['GET'])
    def get_users_route():
        return get_users()
    
    @user_bp.route('/<string:user_id>', methods=['GET'])
    def get_user_route(user_id):
        return get_user(user_id)
    
    @user_bp.route('/update-admin/<string:user_id>', methods=['PUT'])
    def update_user_admin_route(user_id):
        return update_user_admin(user_id)
    
    return user_bp