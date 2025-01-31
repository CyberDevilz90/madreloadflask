from flask import Blueprint, request
from apps.margin.functions import updateMargin
from apps.utils.functions import getMargin

margin = Blueprint('margin', __name__)

@margin.route('/get-margin', methods=['GET'])
def _1():
    return getMargin()

@margin.route('/update-margin', methods=['POST'])
def _2():
    try:
        request_data = request.json  # Fetching data dari body permintaan
        if not request_data:
            return {"error": "No JSON payload provided"}, 400
        return updateMargin(request_data)
    except Exception as e:
        print("Error in updateMargin: %s", e)
        return {"error": str(e)}, 500
    