# models.py
from apps import db

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    telp = db.Column(db.String(50), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    token = db.Column(db.String, nullable=False)
    saldo = db.Column(db.Integer, nullable=False, default=0)

class TransactionSocialMedia(db.Model):
    __tablename__ = 'transaction_social_media'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_pesanan = db.Column(db.Integer, unique=True, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('product_social_media.id'), nullable=False)
    service_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    start_count = db.Column(db.String, nullable=False)
    remains = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    tanggal_order = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class RefID(db.Model):
    __tablename__ = 'ref_id'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False, unique=True)

class TransactionPPOB(db.Model):
    __tablename__ = 'transaction_ppob'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id_pesanan = db.Column(db.Integer, unique=True, nullable=False)
    product_name = db.Column(db.String, nullable=False)
    ref_id = db.Column(db.String, db.ForeignKey('ref_id.code'), nullable=False)
    customer_no = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    buyer_sku_code = db.Column(db.String, db.ForeignKey('product_ppob.buyer_sku_code'), nullable=False)
    message = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    sn = db.Column(db.String, nullable=False)
    tanggal_order = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

class ProductSocialMedia(db.Model):
    __tablename__ = 'product_social_media'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    min = db.Column(db.Integer, nullable=False)
    max = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    jenis = db.Column(db.String, nullable=False)

class ProductPPOB(db.Model):
    __tablename__ = 'product_ppob'
    buyer_sku_code = db.Column(db.String, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String, nullable=False)
    brand = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    seller_name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    buyer_product_status = db.Column(db.String, nullable=False)
    seller_product_status = db.Column(db.String, nullable=False)
    multi = db.Column(db.String, nullable=False)
    desc = db.Column(db.String, nullable=False)

class MarginOmset(db.Model):
    __tablename__ = 'margin_omset'
    id = db.Column(db.Integer, primary_key=True)
    pulsa = db.Column(db.Integer, nullable=False, default=5)
    game = db.Column(db.Integer, nullable=False, default=5)
    social_media = db.Column(db.Integer, nullable=False, default=5)
    ewallet = db.Column(db.Integer, nullable=False, default=5)
    voucher = db.Column(db.Integer, nullable=False, default=5)
    pln = db.Column(db.Integer, nullable=False, default=5)
    paket_data = db.Column(db.Integer, nullable=False, default=5)
