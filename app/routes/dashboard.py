from flask import Blueprint

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def dashboard():
    return 'Dashboard Page'
