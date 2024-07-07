from flask import Blueprint
from apps.product.functions import listProduct, listSocialMedia
from apps.utils.functions import refreshPPOB, refreshSocialMedia

product = Blueprint('product', __name__)

@product.route('/refresh-ppob', methods=['GET'])
def _1():
    return refreshPPOB()

@product.route('/list-ppob', methods=['GET'])
def _2():
    return listProduct()

@product.route('/refresh-social-media', methods=['GET'])
def _3():
    return refreshSocialMedia()

@product.route('/list-social-media', methods=['GET'])
def _4():
    return listSocialMedia()