from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.secret_key = 'your-secret-key'

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to register them with SQLAlchemy
    from . import models

    
    # (Optional) import and register blueprints here
    # from .routes import main as main_blueprint
    # app.register_blueprint(main_blueprint)
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app
