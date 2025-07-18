from flask import Blueprint, render_template, session, redirect, url_for, request
from app.models import db, Update, User, Project

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Optional filters from query params
    search_name = request.args.get('name', '').strip()
    search_project = request.args.get('project', '').strip()
    search_location = request.args.get('location', '').strip()
    search_week = request.args.get('week', '').strip()

    # Base query
    query = db.session.query(Update).join(User).join(Project)

    # Apply filters
    if search_name:
        query = query.filter(User.name.contains(search_name))
    if search_project:
        query = query.filter(Project.project_name.contains(search_project))
    if search_location:
        query = query.filter(Project.location.contains(search_location))
    if search_week:
        query = query.filter(Update.week == search_week)

    updates = query.all()

    return render_template(
        'dashboard.html',
        updates=updates,
        filters={
            'name': search_name,
            'project': search_project,
            'location': search_location,
            'week': search_week
        }
    )
