from flask import Blueprint, jsonify
from app.models import Project

bp = Blueprint('api', __name__)

@bp.route('/api/projects')
def api_projects():
    projects = Project.query.order_by(Project.project_name).all()
    return jsonify([
        {
            'id': p.id,
            'project_name': p.project_name,
            'location': p.location
        } for p in projects
    ])
