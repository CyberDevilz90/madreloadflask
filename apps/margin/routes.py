from flask import Blueprint, request
from apps.margin.functions import updateMargin
from apps.utils.functions import getMargin

margin = Blueprint('margin', __name__)

@margin.route('/get-margin', methods=['GET'])
def _1():
    return getMargin()

@margin.route('/update-margin', methods=['POST'])
def _2():
    request_data = request.json  # Dapatkan data dari badan permintaan
    return updateMargin(request_data)