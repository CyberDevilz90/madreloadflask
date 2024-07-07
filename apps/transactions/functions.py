import requests
import hashlib
from flask import jsonify, request
from datetime import datetime
from apps import db
from apps.models import ProductPPOB, TransactionPPOB, RefID
from apps.utils.functions import create_ref_id, generate_sign

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

        username = "biduguopZ9GW"
        api_key = "a8beff67-cb39-5be2-b4cf-afe22f7e0bab"
        # api_key = "dev-9790e880-5ce5-11ec-af18-b53e1be9e9ea"

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

        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                transaction_data = data['data']
                product = ProductPPOB.query.filter_by(buyer_sku_code=buyer_sku_code).first()
                new_transaction = TransactionPPOB(
                    user_id=user_id,
                    product_name=product.product_name if product else "",
                    ref_id=ref_id,
                    customer_no=customer_no,
                    price=transaction_data['price'],
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