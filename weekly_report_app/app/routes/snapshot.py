from flask import Blueprint

bp = Blueprint('snapshot', __name__, url_prefix='/snapshot')

@bp.route('/')
def snapshot_home():
    return "Snapshot Page"
