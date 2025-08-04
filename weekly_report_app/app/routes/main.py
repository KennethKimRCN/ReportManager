from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .models import (
    db, Report, OtherNote, PersonalSchedule, Companion, SolutionItem,
    Project, ProjectUpdate, SalesSupport, SalesSupportCompanion, User
)
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.filter_by(user_id=current_user.id).order_by(Report.week_start.desc()).all()
    return render_template('dashboard.html', reports=reports)


@main.route('/report/edit/<int:report_id>')
@login_required
def edit_report(report_id):
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()
    all_projects = Project.query.all()
    solution_names = sorted(set([p.solution_name for p in all_projects]))
    return render_template('edit_report.html', report=report, projects=all_projects, solutions=solution_names)


@main.route('/report/update', methods=['POST'])
@login_required
def update_report():
    report_id = int(request.form.get('report_id'))
    report = Report.query.filter_by(id=report_id, user_id=current_user.id).first_or_404()

    # Notes
    note_text = request.form.get('note', '').strip()
    if report.other_notes_entries:
        report.other_notes_entries[0].note = note_text
    elif note_text:
        note = OtherNote(report_id=report.id, note=note_text)
        db.session.add(note)

    # Clear existing schedules
    PersonalSchedule.query.filter_by(report_id=report.id).delete()
    db.session.flush()

    categories = request.form.getlist('schedule_category[]')
    titles = request.form.getlist('schedule_title[]')
    locations = request.form.getlist('schedule_location[]')
    starts = request.form.getlist('schedule_start[]')
    ends = request.form.getlist('schedule_end[]')
    descriptions = request.form.getlist('schedule_description[]')

    schedules = []
    for i in range(len(categories)):
        schedule = PersonalSchedule(
            report_id=report.id,
            category=categories[i],
            title=titles[i],
            location=locations[i],
            start_date=datetime.strptime(starts[i], '%Y-%m-%d'),
            end_date=datetime.strptime(ends[i], '%Y-%m-%d'),
            description=descriptions[i]
        )
        schedules.append(schedule)
        db.session.add(schedule)

    # Companions
    companions_input = request.form.getlist('companions[]')
    for i, comp_input in enumerate(companions_input):
        if i >= len(schedules): break
        names = [n.strip() for n in comp_input.split(',') if n.strip()]
        for name in names:
            companion = Companion(name=name, personal_schedule=schedules[i])
            db.session.add(companion)

    # Clear existing solution items
    for item in report.solution_items:
        db.session.delete(item)
    db.session.flush()

    solution_names = request.form.getlist('solution_name[]')
    project_ids = request.form.getlist('project_id[]')
    project_names = request.form.getlist('project_name[]')
    project_progresses = request.form.getlist('project_progress[]')
    assignee_inputs = request.form.getlist('project_assignees[]')

    solution_map = {}
    for i, sol_name in enumerate(solution_names):
        if sol_name not in solution_map:
            solution = SolutionItem(name=sol_name, report=report)
            db.session.add(solution)
            solution_map[sol_name] = solution

    # Projects & Updates
    for i in range(len(project_names)):
        sol_name = solution_names[min(i, len(solution_names)-1)]
        solution = solution_map[sol_name]

        if i < len(project_ids) and project_ids[i]:
            # Use existing project
            project = Project.query.get(int(project_ids[i]))
        else:
            # New project
            project = Project(
                solution_item=solution,
                solution_name=sol_name,
                company="N/A",
                location="N/A",
                project_name=project_names[i],
                code=f"{sol_name}-{project_names[i]}-{report.id}-{i}"
            )
            db.session.add(project)

        update = ProjectUpdate(
            project=project,
            progress=project_progresses[i]
        )
        db.session.add(update)

        # Assignees
        if i < len(assignee_inputs):
            ids = [emp.strip() for emp in assignee_inputs[i].split(',') if emp.strip()]
            for eid in ids:
                user = User.query.filter_by(employee_id=eid).first()
                if user and user not in update.assignees:
                    update.assignees.append(user)

    report.updated_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('main.dashboard'))
