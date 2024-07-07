from flask import Blueprint
from apps.transactions.functions import perform_transaction_ppob

transactions = Blueprint('transactions', __name__)

@transactions.route('/create-order', methods=['POST'])
def handle_perform_transaction():
    return perform_transaction_ppob()