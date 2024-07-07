import requests
from apps.models import TransactionPPOB
from flask import jsonify, request
from apps import db
from apps.utils.functions import generate_sign

DIGIFLAZZ_API_URL = 'https://api.digiflazz.com/v1/transaction'
DIGIFLAZZ_API_KEY = 'a8beff67-cb39-5be2-b4cf-afe22f7e0bab'
DIGIFLAZZ_USERNAME = 'biduguopZ9GW'

def getHistoryPPOB(user_id):
    try:
        ppob = TransactionPPOB.query.filter_by(user_id=user_id).all()
        
        ppob_data = []
        for i in ppob:
            ppob_data.append({
                'id': i.id,
                'product_name': i.product_name,
                'ref_id': i.ref_id,
                'customer_no': i.customer_no,
                'buyer_sku_code': i.buyer_sku_code,
                'price': i.price,
                'status': i.status,
                'tanggal_order': i.tanggal_order
            })
            
        return ppob_data, 200
    
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
    
def getTransactionStatus(body):
        payload = {            
            'username': DIGIFLAZZ_USERNAME,
            'buyer_sku_code': body.get("buyer_sku_code"),
            'customer_no': body.get("customer_no"),
            'ref_id': body.get("ref_id"),
            'sign': generate_sign(DIGIFLAZZ_USERNAME, DIGIFLAZZ_API_KEY, body.get("ref_id"))
            }

        try:
            response = requests.post(DIGIFLAZZ_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('status')
        except requests.RequestException as e:
            print(f'Error fetching {e}')