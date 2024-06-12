from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    bcrypt = Bcrypt(app) 
    app.config.from_object(Config)

    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)


    # Import and register blueprints
    from apps.user.routes import user as user_blueprint
    from apps.product.routes import product as product_blueprint
    from apps.margin.routes import margin as margin_blueprint
    from apps.utils.routes import utils as utils_blueprint

    app.register_blueprint(user_blueprint, url_prefix='/user')
    app.register_blueprint(product_blueprint, url_prefix='/product')
    app.register_blueprint(margin_blueprint, url_prefix='/margin')
    app.register_blueprint(utils_blueprint, url_prefix='/utils')
    
    with app.app_context():
        db.create_all()

    return app
