import requests
from flask import jsonify
from apps import db
from apps.models import ProductPPOB
from apps.models import MarginOmset

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
        "username": "biduguopZ9GW",
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