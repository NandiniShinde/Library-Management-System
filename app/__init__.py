from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .routes import configure_routes

db = SQLAlchemy()

def create_app(config_name="development"):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Configure routes
    configure_routes(app)  
    
    return app
