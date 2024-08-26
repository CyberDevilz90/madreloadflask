import requests
import hashlib
from flask import jsonify, request
from datetime import datetime
from apps import db
from apps.models import ProductPPOB, ProductSocialMedia, TransactionPPOB, TransactionSocialMedia, RefID, User
from apps.utils.functions import create_ref_id, generate_sign

DIGIFLAZZ_API_URL = 'https://api.digiflazz.com/v1/transaction'
DIGIFLAZZ_API_KEY = 'a8beff67-cb39-5be2-b4cf-afe22f7e0bab'
# DIGIFLAZZ_API_KEY = "dev-9790e880-5ce5-11ec-af18-b53e1be9e9ea"
DIGIFLAZZ_USERNAME = 'biduguopZ9GW'

BUZZERPANEL_URL = 'https://buzzerpanel.id/api/json.php'
BUZZERPANEL_API_KEY = 'kl1fvb5pa4z9te3082su7qrxjcmd6o'
BUZZERPANEL_SECRET_KEY = 'uYJQ4cMAanFijWO17egthwNGp53HVkBx0PfRS8Kmo9lE2dIrvD'


def perform_transaction_ppob():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        buyer_sku_code = data.get('buyer_sku_code')
        customer_no = data.get('customer_no')
        user_id = data.get('user_id')  # Assuming user_id is passed in the request JSON

        if not buyer_sku_code or not customer_no or not user_id:
            return jsonify({"error": "Missing required fields"}), 400

        username = DIGIFLAZZ_USERNAME
        api_key = DIGIFLAZZ_API_KEY

        # Generate ref_id using create_ref_id function
        ref_id = create_ref_id()

        sign = generate_sign(username, api_key, ref_id)

        url = "https://api.digiflazz.com/v1/transaction"
        payload = {
            "username": username,
            "buyer_sku_code": buyer_sku_code,
            "customer_no": customer_no,
            "ref_id": ref_id,
            "sign": sign
        }
        
        # Fetch the product to get the price
        product = ProductPPOB.query.filter_by(buyer_sku_code=buyer_sku_code).first()
        if not product:
            return jsonify({"error": "Invalid buyer_sku_code"}), 400

        product_price = product.price

        response = requests.post(url, json=payload)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.saldo < product_price:
            return jsonify({"error": "Insufficient balance"}), 400

        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                transaction_data = data['data']
                user.saldo -= product_price
                new_transaction = TransactionPPOB(
                    user_id=user_id,
                    product_name=product.product_name if product else "",
                    ref_id=ref_id,
                    customer_no=customer_no,
                    price=product_price,
                    buyer_sku_code=buyer_sku_code,
                    message=transaction_data['message'],
                    status=transaction_data['status'],
                    sn=transaction_data.get('sn', ''),
                    tanggal_order=datetime.now()
                )

                db.session.add(new_transaction)
                db.session.commit()
                return jsonify({"status": "success", "data": transaction_data}), 200
            else:
                return jsonify({"error": "Invalid response from API"}), 500
        else:
            return jsonify({"error": "Failed to perform transaction", "details": response.text}), response.status_code

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    
def perform_transaction_sosmed():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No Data"}), 400
        
        user_id = data.get('user_id')
        service = data.get('service')  
        destination = data.get('destination')  
        quantity = data.get('quantity')
        price = data.get('price')
        
        if not user_id or not service or not quantity or not destination:
            return jsonify({"error": "Missing required fields"}), 400
        
        post_data = {
            'api_key': BUZZERPANEL_API_KEY,
            'secret_key': BUZZERPANEL_SECRET_KEY,
            'action': 'order',
            'service': service,
            'data': destination,  
            'quantity': quantity
        }
        
        response = requests.post(BUZZERPANEL_URL, data=post_data)
        response.raise_for_status()
        
        api_response = response.json()
        
        if not api_response.get('status'):
            return jsonify({"error": "Failed to create order"}), 400

        order_id = api_response.get('data', {}).get('id')

        if not order_id:
            return jsonify({"error": "Order ID not returned from API"}), 500
        
        product = ProductSocialMedia.query.filter_by(id=service).first()
        if not product:
            return jsonify({"error": "Invalid service ID"}), 400

        service_name = product.name
        
        new_transaction = TransactionSocialMedia(
            user_id=user_id,
            service_id=service,
            service_name=service_name,
            price=price,
            start_count=0,
            remains=quantity,
            status='pending',
            id_pesanan=order_id,
            data=destination,
            quantity=quantity,
            tanggal_order=datetime.now()
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return jsonify({"status": "success", "data": api_response}), 200

    except requests.RequestException as e:
        return jsonify({"error": "API request failed", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500