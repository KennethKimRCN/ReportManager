from flask import Blueprint, render_template, session, redirect, url_for
from app.models import Report, User
from app.utils.date_utils import get_sunday_of_current_week
from app.utils.report_utils import generate_weekly_reports_if_missing

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    # Redirect to login if user not logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    # Get the start date (Sunday) of the current week
    week_start = get_sunday_of_current_week()

    # Lazy trigger: Generate weekly reports if they are missing
    generate_weekly_reports_if_missing()

    if user.is_manager:
        # Manager view: list employees (non-managers) and their reports for current week
        employees = User.query.filter_by(is_manager=False).all()
        reports = Report.query.filter_by(week_start=week_start).all()

        return render_template(
            'dashboard.html',
            is_manager=True,
            employees=employees,
            reports=reports,
            week_label=week_start.strftime('Y%yW%U'),  # e.g. Y25W30
            current_week=week_start,
            submitted_count=len(reports),
            total_users=len(employees),
            available_weeks=[],  # You can implement this later to show selectable weeks
        )
    else:
        # Employee view: only show their own reports (ordered by week descending)
        reports = Report.query.filter_by(user_id=user.id).order_by(Report.week_start.desc()).all()
        return render_template(
            'dashboard.html',
            is_manager=False,
            reports=reports
        )
