from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load config
    app.config.from_mapping(
        SECRET_KEY='your-super-secret-key',  # Change for production
        SQLALCHEMY_DATABASE_URI='sqlite:///weekly_report.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # Load instance config if exists
    if os.path.exists(os.path.join(app.instance_path, 'config.py')):
        app.config.from_pyfile('config.py', silent=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from . import models

    # Register Blueprints directly (no init_routes needed)
    from .routes import auth, dashboard, project, report  # , export
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(report.bp)
    # app.register_blueprint(export.bp)

    return app