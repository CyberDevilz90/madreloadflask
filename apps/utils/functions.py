import os
import requests
import hashlib
from flask import jsonify, request
from apps import db, create_app
from apps.models import ProductPPOB, ProductSocialMedia, TransactionPPOB, MarginOmset, RefID
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
current_date = datetime.now().strftime("%d%m%Y")
counter = 0

DIGIFLAZZ_API_URL = os.getenv('DIGIFLAZZ_API_URL')
DIGIFLAZZ_API_KEY = os.getenv('DIGIFLAZZ_API_KEY')
# DIGIFLAZZ_API_KEY = os.getenv()
DIGIFLAZZ_USERNAME = os.getenv('DIGIFLAZZ_USERNAME')

BUZZERPANEL_URL = os.getenv('BUZZERPANEL_URL')
BUZZERPANEL_API_KEY = os.getenv('BUZZERPANEL_API_KEY')
BUZZERPANEL_SECRET_KEY = os.getenv('BUZZERPANEL_SECRET_KEY')

def getMargin():
    try:
        margin = MarginOmset.query.all()

        margin_data = []
        for i in margin:
            margin_data.append({
                'pulsa': i.pulsa,
                'game': i.game,
                'social_media': i.social_media,
                'ewallet': i.ewallet,
                'voucher': i.voucher,
                'pln': i.pln,
                'paket_data': i.paket_data,
            })

        return margin_data, 200
    
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

def refreshPPOB():
# External API endpoint and request payload
    url = 'https://api.digiflazz.com/v1/price-list'
    payload = {
        "cmd" : "prepaid",
        "username": DIGIFLAZZ_USERNAME,
        "sign": "31c39f657218b2066b9ab907fe1361aa"
            }

    try:
        # Send a POST request to the external API
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Ensure the response contains the expected data
        if 'data' in data:
            products = data['data']

            # Clear existing data in the ProductPPOB table
            ProductPPOB.query.delete()

           # Get margin data
            margin_data, status_code = getMargin()
            if status_code == 200:
                margin = margin_data[0]  # Assuming there is only one margin data
            else:
                return jsonify(margin_data), status_code  # Return the error response
            
            # Iterate over the products and insert them into the database
            for item in products:
                if item['category'] == 'Pulsa':
                    price = item['price'] + margin['pulsa']
                elif item['category'] == 'Games':
                    price = item['price'] + item['price']*margin['game']/100
                elif item['category'] == 'E-Money':
                    price = item['price'] + margin['ewallet']
                elif item['category'] == 'Voucher':
                    price = item['price'] + margin['voucher']
                elif item['category'] == 'PLN':
                    price = item['price'] + margin['pln']
                elif item['category'] == 'Data':
                    price = item['price'] + margin['paket_data']
                else:
                    price = item['price']

                product = ProductPPOB(
                    buyer_sku_code=item['buyer_sku_code'],
                    product_name=item['product_name'],
                    category=item['category'],
                    brand=item['brand'],
                    type=item['type'],
                    seller_name=item['seller_name'],
                    price=price,
                    buyer_product_status=item['buyer_product_status'],
                    seller_product_status=item['seller_product_status'],
                    multi=item['multi'],
                    desc=item['desc']
                )
                db.session.add(product)

            # Commit the changes to the database
            db.session.commit()

            return jsonify({'status': 'success', 'data': products}), 200

        else:
            return jsonify({'status': 'error', 'message': 'Unexpected response format'}), 500

    except requests.exceptions.RequestException as e:
        # Handle any errors from the HTTP request
        return jsonify({'status': 'error', 'message': str(e)}), 500

def refreshSocialMedia():
    url = BUZZERPANEL_URL
    payload = {
        'api_key' : BUZZERPANEL_API_KEY,
        'secret_key' : BUZZERPANEL_SECRET_KEY,
        'action' : 'services'
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        data = response.json()
        
        if "data" in data:
            products = data["data"]
            
            ProductSocialMedia.query.delete()
            
            margin_data, status_code = getMargin()
            if status_code == 200:
                margin = margin_data[0]
            else:
                return jsonify(margin_data), status_code
            
            for item in products:
                price_int = int(item['price'])
                new_price_int = price_int + price_int * margin['social_media'] / 100
                price_str = str(int(new_price_int))
                
                product = ProductSocialMedia(
                id=item['id'],
                name=item['name'],
                price=price_str,
                min=item['min'],
                max=item['max'],
                note=item['note'],
                category=item['category'],
                jenis=item['jenis'],
                )
                db.session.add(product)
        
            db.session.commit()
        
            return jsonify({'status': 'success', 'data': products}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Unexpected response'})
    
    except requests.exceptions.RequestException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
            

def proxy_buzzer():
    url_buzzerpanel = BUZZERPANEL_URL
    body_buzzerpanel = {
        "api_key": BUZZERPANEL_API_KEY,
        "secret_key": BUZZERPANEL_SECRET_KEY,
        "action": "profile"
    }
    try:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(url_buzzerpanel, data=body_buzzerpanel, headers=headers)
        print("Request Body:", body_buzzerpanel)
        print("API Response:", response.text)
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
def proxy_digiflazz():
    url_digiflazz = "https://api.digiflazz.com/v1/cek-saldo"
    body_digiflazz = {
        "cmd": "deposit",
        "username": DIGIFLAZZ_USERNAME,
        "sign": generate_sign(DIGIFLAZZ_USERNAME, DIGIFLAZZ_API_KEY, "depo")
    }
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url_digiflazz, json=body_digiflazz, headers=headers)
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
def handle_input_completion():
    try:
        data = request.get_json()
        user_id = data.get('userId')

        request_data = {
            "username": DIGIFLAZZ_USERNAME,
            "customer_no": user_id,
            "sign": generate_sign(DIGIFLAZZ_USERNAME, DIGIFLAZZ_API_KEY, user_id)
        }
        response = requests.post("https://api.digiflazz.com/v1/inquiry-pln", json=request_data, headers={
            "Content-Type": "application/json"
        })
        response.raise_for_status()
        return jsonify(response.json()), response.status_code

    except requests.RequestException as e:
        # Tangani kesalahan jika terjadi
        return jsonify({"error": str(e)}), 500
    
def create_ref_id():
    global current_date
    global counter

    # Mendapatkan tanggal saat ini
    today_date = datetime.now().strftime("%d%m%Y")

    # Reset counter jika tanggal berubah
    if today_date != current_date:
        current_date = today_date
        counter = 0

    # Loop untuk mencoba membuat ref_id yang unik
    while True:
        # Increment counter
        counter += 1

        # Membuat ref_id dengan format MR+tanggal-bulan-tahun+x
        ref_id = f"MR{today_date}{counter:05d}"

        # Cek apakah ref_id sudah ada di database
        if not db.session.query(RefID).filter_by(code=ref_id).first():
            # Jika tidak ada, simpan ref_id baru
            new_ref_id = RefID(code=ref_id)
            db.session.add(new_ref_id)
            try:
                db.session.commit()
                return ref_id
            except Exception:
                # Jika terjadi duplikasi di commit, rollback dan coba lagi
                db.session.rollback()
        # Jika sudah ada, lanjutkan loop untuk mencoba ref_id baru
        
def generate_sign(username, api_key, ref_id):
    sign_str = f"{username}{api_key}{ref_id}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    return sign