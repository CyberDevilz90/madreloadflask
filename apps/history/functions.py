import os
import requests
from apps.models import TransactionPPOB, TransactionSocialMedia
from flask import jsonify, request
from apps import db
from apps.utils.functions import generate_sign
from dotenv import load_dotenv
load_dotenv()

DIGIFLAZZ_API_URL = os.getenv('DIGIFLAZZ_API_URL')
DIGIFLAZZ_API_KEY = os.getenv('DIGIFLAZZ_API_KEY')
# DIGIFLAZZ_API_KEY = os.getenv()
DIGIFLAZZ_USERNAME = os.getenv('DIGIFLAZZ_USERNAME')

BUZZERPANEL_URL = os.getenv('BUZZERPANEL_URL')
BUZZERPANEL_API_KEY = os.getenv('BUZZERPANEL_API_KEY')
BUZZERPANEL_SECRET_KEY = os.getenv('BUZZERPANEL_SECRET_KEY')

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
                'sn': i.sn,
                'tanggal_order': i.tanggal_order
            })
            
        return ppob_data, 200
    
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
    
def getHistorySSM(user_id):
    try:
        ssm = TransactionSocialMedia.query.filter_by(user_id=user_id).all()
        
        ssm_data = []
        for i in ssm:
            ssm_data.append({
                'id': i.id,
                'service_id': i.service_id,
                'service_name': i.service_name,
                'price': i.price,
                'start_count': i.start_count,
                'remains': i.remains,
                'status': i.status,
                'tanggal_order': i.tanggal_order,
                'data': i.data,
                'quantity': i.quantity,
            })
            
        return ssm_data, 200
    
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