import os

root = 'REPORTMANAGER'

structure = [
    'app',
    'app/routes',
    'app/templates',
    'app/static/css',
    'app/static/js',
    'migrations'
]

files = {
    'run.py': """from app import create_app\n\napp = create_app()\n\nif __name__ == '__main__':\n    app.run(debug=True)\n""",

    'config.py': """class Config:\n    SECRET_KEY = 'dev'  # Change this in production\n    SQLALCHEMY_DATABASE_URI = 'sqlite:///weekly_report.db'\n    SQLALCHEMY_TRACK_MODIFICATIONS = False\n""",

    'requirements.txt': "flask\nflask_sqlalchemy\nflask_migrate\n",

    'app/__init__.py': """from flask import Flask\nfrom flask_sqlalchemy import SQLAlchemy\nfrom flask_migrate import Migrate\n\ndb = SQLAlchemy()\nmigrate = Migrate()\n\ndef create_app():\n    app = Flask(__name__)\n    app.config.from_object('config.Config')\n\n    db.init_app(app)\n    migrate.init_app(app, db)\n\n    from .routes import auth, dashboard, report, project\n    app.register_blueprint(auth.bp)\n    app.register_blueprint(dashboard.bp)\n    app.register_blueprint(report.bp)\n    app.register_blueprint(project.bp)\n\n    return app\n""",

    'app/models.py': "# models will be added next step\n",

    'app/routes/__init__.py': "",

    'app/routes/auth.py': "from flask import Blueprint\n\nbp = Blueprint('auth', __name__)\n\n@bp.route('/login')\ndef login():\n    return 'Login Page'\n",

    'app/routes/dashboard.py': "from flask import Blueprint\n\nbp = Blueprint('dashboard', __name__)\n\n@bp.route('/')\ndef dashboard():\n    return 'Dashboard Page'\n",

    'app/routes/project.py': "from flask import Blueprint\n\nbp = Blueprint('project', __name__)\n\n@bp.route('/project')\ndef project():\n    return 'Project Page'\n",

    'app/routes/report.py': "from flask import Blueprint\n\nbp = Blueprint('report', __name__)\n\n@bp.route('/report')\ndef report():\n    return 'Report Page'\n",

    'app/templates/base.html': "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"UTF-8\">\n  <title>{% block title %}Weekly Report{% endblock %}</title>\n  <link rel=\"stylesheet\" href=\"/static/css/style.css\">\n</head>\n<body>\n  {% block content %}{% endblock %}\n</body>\n</html>",

    'app/templates/login.html': "{% extends 'base.html' %}\n{% block title %}Login{% endblock %}\n{% block content %}<h1>Login</h1>{% endblock %}",

    'app/templates/dashboard.html': "{% extends 'base.html' %}\n{% block title %}Dashboard{% endblock %}\n{% block content %}<h1>Dashboard</h1>{% endblock %}",

    'app/templates/create_report.html': "{% extends 'base.html' %}\n{% block title %}Create Report{% endblock %}\n{% block content %}<h1>Create Report</h1>{% endblock %}",

    'app/templates/view_report.html': "{% extends 'base.html' %}\n{% block title %}View Report{% endblock %}\n{% block content %}<h1>View Report</h1>{% endblock %}",

    'app/templates/create_project.html': "{% extends 'base.html' %}\n{% block title %}Create Project{% endblock %}\n{% block content %}<h1>Create Project</h1>{% endblock %}",

    'app/static/css/style.css': "body { font-family: Arial, sans-serif; background: #f9f9f9; }",

    'app/static/js/main.js': "console.log('JS loaded');"
}

def create_structure():
    for folder in structure:
        path = os.path.join(root, folder)
        os.makedirs(path, exist_ok=True)
        print(f"Created folder: {path}")

    for file_path, content in files.items():
        full_path = os.path.join(root, file_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {full_path}")

if __name__ == '__main__':
    create_structure()
