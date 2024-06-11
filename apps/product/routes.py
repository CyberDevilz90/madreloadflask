from flask import Blueprint
from apps.product.functions import listProduct
from apps.utils.functions import refreshPPOB

product = Blueprint('product', __name__)

@product.route('/refresh-ppob', methods=['GET'])
def _1():
    return refreshPPOB()

@product.route('/list-ppob', methods=['GET'])
def _2():
    return listProduct()