from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()  # ✅ define here, not in models.py
migrate = Migrate()

def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models  # import AFTER db is initialized

    from .routes import auth, dashboard, report, project
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(project.bp)

    return app
