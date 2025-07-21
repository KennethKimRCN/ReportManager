from flask import Blueprint, render_template, session, redirect, url_for, request, flash, current_app
from datetime import timedelta, datetime
from app import db
from app.models import Report, Project, ProjectUpdate, PersonalSchedule, User
from app.utils.date_utils import get_sunday_of_current_week
from app.utils.snapshot_utils import ensure_snapshot_for_project
from app.utils.diff_utils import compare_project_updates

bp = Blueprint('report', __name__, url_prefix='/report')

# 🔧 Helper to serialize project for JSON
def serialize_project(project):
    return {
        'id': project.id,
        'project_name': project.project_name,
        'solution_name': project.solution_name
    }

@bp.route('/edit', methods=['GET', 'POST'])
def edit_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    week_start = get_sunday_of_current_week()
    week_end = week_start + timedelta(days=6)

    report = Report.query.filter_by(user_id=user_id, week_start=week_start).first()
    if not report:
        report = Report(user_id=user_id, week_start=week_start, week_end=week_end, status='Draft')
        db.session.add(report)
        db.session.commit()

    user = User.query.get(user_id)
    assigned_projects = user.assigned_projects
    all_projects = Project.query.order_by(Project.solution_name).all()

    if request.method == 'POST':
        status = request.form.get('status')
        report.status = status
        report.week_end = week_end
        report.submitted_at = datetime.utcnow() if status == 'Submitted' else None
        db.session.commit()

        ProjectUpdate.query.filter_by(report_id=report.id).delete()
        project_ids = request.form.getlist('project_id[]')
        progress_list = request.form.getlist('progress[]')
        issue_list = request.form.getlist('issue[]')
        sales_list = request.form.getlist('sales_support[]')
        other_list = request.form.getlist('other_note[]')

        for i in range(len(project_ids)):
            progress = progress_list[i].strip()
            if progress:  # Required field
                update = ProjectUpdate(
                    report_id=report.id,
                    project_id=int(project_ids[i]),
                    progress=progress,
                    issue=issue_list[i],
                    sales_support=sales_list[i],
                    other_note=other_list[i]
                )
                db.session.add(update)

        PersonalSchedule.query.filter_by(report_id=report.id).delete()
        categories = request.form.getlist('schedule_category[]')
        titles = request.form.getlist('schedule_title[]')
        locations = request.form.getlist('schedule_location[]')
        start_dates = request.form.getlist('schedule_start_date[]')
        end_dates = request.form.getlist('schedule_end_date[]')
        descriptions = request.form.getlist('schedule_description[]')

        for category, title, location, start_date, end_date, description in zip(
            categories, titles, locations, start_dates, end_dates, descriptions
        ):
            if all([category.strip(), title.strip(), location.strip(), start_date.strip(), end_date.strip()]):
                ps = PersonalSchedule(
                    report_id=report.id,
                    category=category,
                    title=title,
                    location=location,
                    start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                    end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
                    description=description or ''
                )
                db.session.add(ps)

        db.session.commit()
        flash("보고서가 저장되었습니다.")
        return redirect(url_for('dashboard.index'))

    return render_template(
        'create_report.html',
        report=report,
        assigned_projects=[serialize_project(p) for p in assigned_projects],
        all_projects=[serialize_project(p) for p in all_projects],
        edit_mode=True
    )



@bp.route('/view/<int:report_id>')
def view_report(report_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    report = Report.query.get_or_404(report_id)

    if not session.get('is_manager') and report.user_id != session['user_id']:
        flash('접근 권한이 없습니다.')
        return redirect(url_for('dashboard.index'))

    project_diffs = compare_project_updates(report)

    return render_template('view_report.html', report=report, diffs=project_diffs)
