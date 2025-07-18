from flask import Blueprint

bp = Blueprint('report', __name__)

@bp.route('/report')
def report():
    return 'Report Page'
