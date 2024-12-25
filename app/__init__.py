from flask import Flask
from .routes import configure_routes
from app.extensions import db  # Import db from extensions


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)  # Important step to register db with the app

    with app.app_context():
        db.create_all()  # Create tables if they don't exist

    # Configure routes
    configure_routes(app)  
    
    return app
