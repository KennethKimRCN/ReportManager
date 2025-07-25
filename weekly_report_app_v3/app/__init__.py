from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    #app.secret_key = 'your-very-secret-key'
    
    # Configure your DB URI here (change to your actual DB)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weekly_report.db'  # or your preferred DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Import models so they get registered
    from . import models  # adjust the import to where your models are
    
    with app.app_context():
        db.create_all()  # Create the tables
    
    return app
