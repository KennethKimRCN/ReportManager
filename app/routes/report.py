from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User, Project, Update, SalesSupport, OtherNote, PersonalSchedule

bp = Blueprint('report', __name__)

@bp.route('/report/create', methods=['GET'])
def create_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    all_projects = Project.query.order_by(Project.project_name).all()

    # Convert each Project object to a dictionary for JSON serialization
    projects_serializable = []
    for p in all_projects:
        projects_serializable.append({
            'id': p.id,
            'solution_name': p.solution_name,
            'company': p.company,
            'location': p.location,
            'project_name': p.project_name,
            'code': p.code
        })
    week_list = [f"Y25W{str(w).zfill(2)}" for w in range(20, 54)]  # Example: Y25W20 ~ Y25W53

    return render_template(
        'create_report.html',
        user=user,
        projects=projects_serializable,
        weeks=week_list
    )

@bp.route('/report/submit', methods=['POST'])
def submit_report():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    week = request.form.get('week')

    # Get or create a default project for personal schedules or missing project_id
    personal_proj = Project.query.filter_by(project_name='Personal Schedule').first()
    if not personal_proj:
        personal_proj = Project(
            solution_name='Internal',
            company='',
            location='',
            project_name='Personal Schedule',
            code='PERSONAL_SCHEDULE'
        )
        db.session.add(personal_proj)
        db.session.commit()

    # 1. Save all project updates
    projects_data = request.form.to_dict(flat=False)
    projects = {}
    for key, value in projects_data.items():
        if key.startswith("projects["):
            # extract index and field name
            idx = key.split("[")[1].split("]")[0]
            field = key.split("]")[1][1:-1]
            projects.setdefault(idx, {})[field] = value[0]

    for idx, p in projects.items():
        project_id_raw = p.get("project_id")
        if not project_id_raw:
            project_id = personal_proj.id
        else:
            project_id = int(project_id_raw)

        progress = p.get("progress")
        project_issues = p.get("project_issues", "").strip()
        sales_support = p.get("sales_support", "").strip()
        other_note = p.get("other_note", "").strip()

        update = Update(
            user_id=user_id,
            project_id=project_id,
            week=week,
            progress=progress,
            project_issues=project_issues
        )
        db.session.add(update)
        db.session.flush()  # Get update.id

        if sales_support:
            db.session.add(SalesSupport(
                update_id=update.id,
                system="N/A",  # could be refined
                company="N/A",
                schedule="N/A",
                content=sales_support,
                companion=""
            ))

        if other_note:
            db.session.add(OtherNote(update_id=update.id, note=other_note))

    # 2. Save personal schedules
    schedules_data = request.form.to_dict(flat=False)
    schedules = {}
    for key, value in schedules_data.items():
        if key.startswith("schedules["):
            idx = key.split("[")[1].split("]")[0]
            field = key.split("]")[1][1:-1]
            schedules.setdefault(idx, {})[field] = value[0]

    for idx, s in schedules.items():
        db.session.add(PersonalSchedule(
            update_id=update.id,  # assign to last update (safe if all same user)
            category=s.get("category"),
            person=s.get("person"),
            location=s.get("location"),
            start_date=s.get("start_date"),
            end_date=s.get("end_date"),
            description=s.get("description")
        ))

    db.session.commit()
    flash("✅ 보고서가 성공적으로 제출되었습니다.", "success")
    return redirect(url_for('dashboard.dashboard'))