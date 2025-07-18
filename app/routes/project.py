from flask import Blueprint

bp = Blueprint('project', __name__)

@bp.route('/project')
def project():
    return 'Project Page'
