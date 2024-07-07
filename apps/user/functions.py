from flask import jsonify, request
from apps.models import User
from apps import db
from flask_bcrypt import Bcrypt 

import secrets

bcrypt = Bcrypt() 

def generate_unique_token():
    while True:
        token = secrets.token_urlsafe(16)
        # Periksa keunikan token dalam database
        existing_user = User.query.filter_by(token=token).first()
        if not existing_user:
            return token

def hash_password(password):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8') 
    return password_hash

# Fungsi untuk memverifikasi password
def verify_password(password, password_hash):
    return bcrypt.check_password_hash(password_hash, password) 
  
def register(request):
    data = request.get_json()
    # Periksa apakah pengguna sudah ada
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"message": "Email already exists"}), 400

    # Hash password
    hashed_password = hash_password(data['password'])
    telp = data['telp']
    token = generate_unique_token()

    # Buat objek pengguna baru
    new_user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password, 
        token=token, 
        role_id=2, 
        saldo=0,
        telp=telp)
    user_data = {   
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "telp": new_user.telp,
        "saldo": new_user.saldo
        # tambahkan atribut lain yang ingin Anda sertakan
    }
    # Tambahkan pengguna ke database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "token": token, "data": user_data})

def login(request):
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and verify_password(data['password'], user.password):
        user_data = {
            "email": user.email,
            "role": user.role_id,
            "name": user.name,
            "saldo": user.saldo,
            "token": user.token
        }
        return jsonify({"info": user_data, "token": user.token}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

def get_user_by_token():
    token = request.headers.get('Authorization')
    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]  # Ambil token tanpa "Bearer "
    else:
        return jsonify({"message": "Token not provided"}), 401
    
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "telp": user.telp,
        "saldo": user.saldo,
        "role": user.role_id,
    }
    return user_data