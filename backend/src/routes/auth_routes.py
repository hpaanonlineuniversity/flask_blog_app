from flask import Blueprint
from ..controllers.auth_controller import signup, signin, google_auth, signout


def create_auth_blueprint(user_model):
    auth_bp = Blueprint('auth', __name__)
    
    @auth_bp.route('/signup', methods=['POST'])
    def signup_route():
        return signup(user_model)
    
    @auth_bp.route('/signin', methods=['POST'])
    def signin_route():
        return signin(user_model)
    
    @auth_bp.route('/google', methods=['POST'])
    def google_route():
        return google_auth(user_model)
    
    @auth_bp.route('/signout', methods=['POST'])
    def signout_route():
        return signout()
    
    return auth_bp