from flask import Blueprint
from apps.transactions.functions import perform_transaction_ppob, perform_transaction_sosmed

transactions = Blueprint('transactions', __name__)

@transactions.route('/create-order', methods=['POST'])
def handle_perform_transaction_ppob():
    return perform_transaction_ppob()

@transactions.route('/create-order-ssm', methods=['POST'])
def handle_perform_transaction_ssm():
    return perform_transaction_sosmed()