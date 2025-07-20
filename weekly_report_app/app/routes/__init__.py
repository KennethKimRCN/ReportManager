from flask import Blueprint

def init_routes(app):
    from . import auth, dashboard, report, project, export, snapshot

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(project.bp)
    app.register_blueprint(export.bp)
    app.register_blueprint(snapshot.bp)
