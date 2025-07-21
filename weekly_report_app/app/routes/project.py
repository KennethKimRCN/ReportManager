from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import Project, ProjectTag, User, ProjectSnapshot
from app import db
from app.utils.date_utils import get_current_week_range
from datetime import date

bp = Blueprint('project', __name__, url_prefix='/project')


@bp.route('/new', methods=['GET', 'POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    tags = ProjectTag.query.all()
    users = User.query.all()

    if request.method == 'POST':
        solution_name = request.form.get('solution_name')
        company = request.form.get('company')
        location = request.form.get('location')
        project_name = request.form.get('project_name')
        code = request.form.get('code')
        #status = request.form.get('status')
        tag_ids = request.form.getlist('tags')
        assignee_ids = request.form.getlist('assignees')

        # Create Project
        project = Project(
            solution_name=solution_name,
            company=company,
            location=location,
            project_name=project_name,
            code=code,
            #status=status,
        )

        # Assign tags and users
        project.tags = ProjectTag.query.filter(ProjectTag.id.in_(tag_ids)).all()
        project.assignees = User.query.filter(User.id.in_(assignee_ids)).all()

        db.session.add(project)
        db.session.commit()

        # Create Snapshot
        week_start, _ = get_current_week_range()
        snapshot = ProjectSnapshot(
            project_id=project.id,
            week_start=week_start,
            solution_name=solution_name,
            company=company,
            location=location,
            project_name=project_name,
            code=code,
            #status=status
        )
        db.session.add(snapshot)
        db.session.commit()

        flash('프로젝트가 등록되었습니다.')
        return redirect(url_for('dashboard.index'))

    return render_template('project_form.html', tags=tags, users=users)
