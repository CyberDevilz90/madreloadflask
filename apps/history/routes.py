from flask import Blueprint, request, jsonify
from apps.history.functions import getHistoryPPOB,getTransactionStatus, getHistorySSM
from apps.user.functions import get_user_by_token

history = Blueprint('history', __name__)

@history.route('/ppob', methods=['GET'])
def get_ppob_history():
    user_data = get_user_by_token()
    
    user_id = user_data['id']
    history_data, status_code = getHistoryPPOB(user_id)
    return jsonify({"data": history_data}), status_code

@history.route('/smm', methods=['GET'])
def get_ppob_smm():
    user_data = get_user_by_token()
    
    user_id = user_data['id']
    history_data, status_code = getHistorySSM(user_id)
    return jsonify({"data": history_data}), status_code

@history.route('/status', methods=['POST'])
def get_status():
    try:
        body = request.get_json()
        if not body:
            return jsonify({'error': 'No JSON data received'}), 400
        
        status = getTransactionStatus(body)
        if status is None:
            return jsonify({'error': 'Failed to fetch transaction status'}), 500
        
        return jsonify({'status': status}), 200
    except Exception as e:
        print(f"Exception occurred: {e}")
        return jsonify({'error': 'Internal server error'}), 500