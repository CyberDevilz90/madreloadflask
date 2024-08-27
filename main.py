from flask import Flask, request
from sqlalchemy import or_
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apps.models import TransactionPPOB, TransactionSocialMedia, db, User
import requests
from apps import create_app
import hashlib

app = create_app()

DIGIFLAZZ_API_URL = 'https://api.digiflazz.com/v1/transaction'
DIGIFLAZZ_API_KEY = 'a8beff67-cb39-5be2-b4cf-afe22f7e0bab'
# DIGIFLAZZ_API_KEY = "dev-9790e880-5ce5-11ec-af18-b53e1be9e9ea"
DIGIFLAZZ_USERNAME = 'biduguopZ9GW'

BUZZERPANEL_API_URL = 'https://buzzerpanel.id/api/json.php'
BUZZERPANEL_API_KEY = 'kl1fvb5pa4z9te3082su7qrxjcmd6o'
BUZZERPANEL_SECRET_KEY = 'uYJQ4cMAanFijWO17egthwNGp53HVkBx0PfRS8Kmo9lE2dIrvD'

def generate_sign(username, api_key, ref_id):
    sign_str = f"{username}{api_key}{ref_id}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign

def update_pending_transactions():
    with app.app_context():
        pending_transactions = TransactionPPOB.query.filter_by(status='Pending').all()
        current_time = datetime.now()
        time_limit = current_time - timedelta(days=89)
     
        # Remove transactions older than 89 days
        old_transactions = TransactionPPOB.query.filter(TransactionPPOB.tanggal_order < time_limit).all()
        for old_transaction in old_transactions:
            db.session.delete(old_transaction)
            
        db.session.commit()
        
        if not pending_transactions:
            print(f"No pending transactions found at {datetime.now()}")
            return  # Exit the function if no pending transactions
        
        for transaction in pending_transactions:
            # Prepare the request payload
            payload = {
                "username": DIGIFLAZZ_USERNAME,
                "buyer_sku_code": transaction.buyer_sku_code,
                "customer_no": transaction.customer_no,
                "ref_id": transaction.ref_id,
                "sign": generate_sign(DIGIFLAZZ_USERNAME, DIGIFLAZZ_API_KEY, transaction.ref_id)
            }
            
            try:
                # Send a POST request to the external API
                response = requests.post("https://api.digiflazz.com/v1/transaction", json=payload)
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                # Parse the JSON response
                data = response.json()
                
                print(f"Response: {data}")  # Debug response
                
                # Check the transaction status
                if 'data' in data:
                    transaction_status = data['data'].get('status')
                    sn = data['data'].get('sn')
                    
                    if transaction_status == 'Sukses':
                        transaction.status = 'Sukses'
                        transaction.sn = sn
                    elif transaction_status == 'Gagal':
                        transaction.status = 'Gagal'
                        
                        user = User.query.get(transaction.user_id)
                        if user:
                            user.balance += transaction.price
                    
                    db.session.commit()
                    
                    print(f"Updated transaction {transaction.id} to status {transaction.status} at {datetime.now()}")
                
            except requests.exceptions.RequestException as e:
                print(f"Error updating transaction {transaction.id}: {e}")
                
def update_pending_smm():
    with app.app_context():
        pending_smm = TransactionSocialMedia.query.filter(
            or_(
                TransactionSocialMedia.status == 'Pending',
                TransactionSocialMedia.status == 'pending',
                TransactionSocialMedia.status == 'In progress',
                TransactionSocialMedia.status == 'Processing'
            )
        ).all()
        
        if not pending_smm:
            print(f"No pending transaction found at {datetime.now()}")
            return
    
        for transaction in pending_smm:
            payload = {
                "action": 'status',
                "api_key": BUZZERPANEL_API_KEY,
                "secret_key": BUZZERPANEL_SECRET_KEY,
                "id": transaction.id_pesanan
            }

            try:
                response = requests.post(BUZZERPANEL_API_URL, data=payload)
                response.raise_for_status()

                data = response.json()
                print(f"Response : {data}")

                if 'data' in data:
                    transaction_status = data['data'].get('status')
                    start_count = data['data'].get('start_count')
                    remains = data['data'].get('remains')

                    if transaction_status == 'Processing':
                        transaction.status = transaction_status
                        transaction.start_count = start_count
                        transaction.remains = remains
                    elif transaction_status == 'In progress':
                        transaction.status = transaction_status
                        transaction.start_count = start_count
                        transaction.remains = remains
                    elif transaction_status == 'Partial':
                        transaction.status = transaction_status
                        transaction.start_count = start_count
                        transaction.remains = remains

                        user = User.query.get(transaction.user_id)
                        if user:
                            sisa = transaction.price/1000 * remains
                            user.balance += sisa

                    db.session.commit()

                    print(f"Updated transaction {transaction.id} to status {transaction.status} at {datetime.now()}")

            except requests.exceptions.RequestException as e:
                print(f"Error updating transaction {transaction.id} : {e}")
            except Exception as e:
                print(f"Unexpected error for transaction {transaction.id}: {e}")

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_pending_transactions, 'interval', minutes=1)
    scheduler.add_job(update_pending_smm, 'interval', minutes=1)
    scheduler.start()
    
    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()