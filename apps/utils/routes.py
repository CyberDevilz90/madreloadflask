from flask import Blueprint, request
from apps.utils.functions import proxy_buzzer, proxy_digiflazz, handle_input_completion

utils = Blueprint('utils', __name__)

@utils.route('/admin-buzzer', methods=['GET'])
def admin_buzzer_route():
    return proxy_buzzer()

@utils.route('/admin-digiflazz', methods=['GET'])
def admin_digiflazz_route():
    return proxy_digiflazz()

@utils.route('/validasi-pln', methods=['POST'])
def handle_input_route():
    return handle_input_completion()