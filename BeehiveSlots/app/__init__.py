from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()

import os
from dotenv import load_dotenv

load_dotenv() # Load .env file

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_dev_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beehive_enterprise.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.owner import owner_bp
    from app.routes.driver import driver_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(driver_bp)
    
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    from app.api import api_bp
    app.register_blueprint(api_bp)
    
    # Init Swagger
    from flasgger import Swagger
    Swagger(app)

    # Database Creation (Dev only)
    with app.app_context():
        # Import models to ensure they are registered with SQLAlchemy
        from app import models
        db.create_all()

    # Import Socket Events
    from app import socket_events

    return app
