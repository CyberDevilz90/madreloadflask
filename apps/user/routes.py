from flask import Blueprint, request
from apps.user.functions import login, register,generate_unique_token,get_user_by_token

user = Blueprint('user', __name__)

@user.route('/login', methods=['POST'])
def login_route():
    return login(request)

@user.route('/register', methods=['POST'])
def register_route():
    return register(request)

@user.route('/generate-token', methods=['GET'])
def generate_token_route():
    return generate_unique_token()

@user.route('/get_user_by_token', methods=['GET'])
def get_user_data_by_token():
    return get_user_by_token()