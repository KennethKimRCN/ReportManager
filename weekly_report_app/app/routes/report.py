from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.models import Project, Report, ProjectUpdate, PersonalSchedule
from app.utils.date_utils import get_current_week_range
from app.utils.snapshot_utils import ensure_snapshot_for_project
from app.utils.diff_utils import compare_project_updates
from app import db
from datetime import datetime, date

bp = Blueprint('report', __name__, url_prefix='/report')


@bp.route('/create', methods=['GET', 'POST'])
def create_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    week_start, week_end = get_current_week_range()

    # Check if report already exists
    existing = Report.query.filter_by(user_id=user_id, week_start=week_start).first()
    if existing:
        flash('이번 주 보고서는 이미 작성되었습니다.')
        return redirect(url_for('dashboard.index'))

    # List only projects assigned to user
    assigned_projects = Project.query \
        .join(Project.assignees) \
        .filter_by(id=user_id) \
        .all()

    if request.method == 'POST':
        status = request.form.get('status')  # Draft or Submitted

        report = Report(
            user_id=user_id,
            week_start=week_start,
            week_end=week_end,
            status=status,
            submitted_at=datetime.utcnow() if status == 'Submitted' else None
        )
        db.session.add(report)
        db.session.flush()  # get report.id

        # <-- Lazy Snapshot Hook added here -->
        for project in assigned_projects:
            ensure_snapshot_for_project(project.id)

        # Save project updates
        for project in assigned_projects:
            prefix = f"project_{project.id}_"
            progress = request.form.get(prefix + "progress")
            issue = request.form.get(prefix + "issue")
            sales = request.form.get(prefix + "sales_support")
            other = request.form.get(prefix + "other_note")

            if progress and progress.strip():
                update = ProjectUpdate(
                    report_id=report.id,
                    project_id=project.id,
                    progress=progress,
                    issue=issue,
                    sales_support=sales,
                    other_note=other
                )
                db.session.add(update)

        # Save personal schedules
        for i in range(1, 6):
            category = request.form.get(f"schedule_{i}_category")
            person = request.form.get(f"schedule_{i}_person")
            if category and person:
                ps = PersonalSchedule(
                    report_id=report.id,
                    category=category,
                    person=person,
                    location=request.form.get(f"schedule_{i}_location"),
                    start_date=request.form.get(f"schedule_{i}_start_date"),
                    end_date=request.form.get(f"schedule_{i}_end_date"),
                    description=request.form.get(f"schedule_{i}_description")
                )
                db.session.add(ps)

        db.session.commit()
        flash("보고서가 저장되었습니다.")
        return redirect(url_for('dashboard.index'))

    return render_template('create_report.html',
                           week_start=week_start,
                           week_end=week_end,
                           assigned_projects=assigned_projects)


@bp.route('/view/<int:report_id>')
def view_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    report = Report.query.get_or_404(report_id)

    # Permission check (manager or owner)
    if not session.get('is_manager') and report.user_id != session['user_id']:
        flash('접근 권한이 없습니다.')
        return redirect(url_for('dashboard.index'))

    project_diffs = compare_project_updates(report)

    return render_template('view_report.html', report=report, diffs=project_diffs)