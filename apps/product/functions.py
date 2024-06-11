from flask import jsonify
from apps.models import ProductSocialMedia,ProductPPOB

def listProduct():
    try:
        # Fetch all data from ProductPPOB table
        products = ProductPPOB.query.all()
        
        # Prepare the data to return as JSON
        products_data = []
        for product in products:
            products_data.append({
                'buyer_sku_code': product.buyer_sku_code,
                'product_name': product.product_name,
                'category': product.category,
                'brand': product.brand,
                'type': product.type,
                'seller_name': product.seller_name,
                'price': product.price,
                'buyer_product_status': product.buyer_product_status,
                'seller_product_status': product.seller_product_status,
                'multi': product.multi,
                'desc': product.desc
            })

        return jsonify({'status': 'success', 'data': products_data}), 200

    except Exception as e:
        # Handle any errors
        return jsonify({'status': 'error', 'message': str(e)}), 500