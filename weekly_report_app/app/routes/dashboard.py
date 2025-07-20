from flask import Blueprint, render_template, session, redirect, url_for
from app.models import Report, User, ProjectUpdate, Project
from app.utils.date_utils import get_current_week_range, get_week_label
from datetime import date, datetime
from app import db
import re

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    is_manager = session.get('is_manager', False)
    today = date.today()
    week_start, week_end = get_current_week_range(today)

    if is_manager:
        # Manager: See reports grouped by user for the current week
        all_reports = Report.query.filter_by(week_start=week_start).all()
        employees = User.query.order_by(User.name).all()
        return render_template('dashboard.html',
                               is_manager=True,
                               employees=employees,
                               reports=all_reports,
                               week_label=get_week_label(week_start))
    else:
        # Employee: See only their own submitted reports
        my_reports = Report.query.filter_by(user_id=user_id).order_by(Report.week_start.desc()).all()
        return render_template('dashboard.html',
                               is_manager=False,
                               reports=my_reports)


# New route for STEP 8: Manager Aggregated View

@bp.route('/project/<int:project_id>/week/<string:week>')
def view_project_week(project_id, week):
    if 'user_id' not in session or not session.get('is_manager'):
        return redirect(url_for('auth.login'))

    # week = e.g. Y25W28
    match = re.match(r'Y(\d{2})W(\d{2})', week)
    if not match:
        return "Invalid week format", 400

    year = int("20" + match.group(1))
    week_num = int(match.group(2))
    # Calculate the week start date (Sunday)
    week_start = datetime.strptime(f'{year}-W{week_num}-0', "%Y-W%W-%w").date()

    updates = ProjectUpdate.query \
        .filter_by(project_id=project_id) \
        .join(Report) \
        .filter(Report.week_start == week_start) \
        .all()

    project = Project.query.get_or_404(project_id)
    return render_template('project_week_view.html', project=project, updates=updates, week=week)
