from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, Project, User

bp = Blueprint('project', __name__)

@bp.route('/project/create', methods=['GET', 'POST'])
def create_project():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    all_users = User.query.order_by(User.name).all()

    if request.method == 'POST':
        project_name = request.form['project_name']
        solution_name = request.form['solution_name']
        company = request.form['company']
        location = request.form['location']
        code = request.form['code']
        assignee_ids = request.form.getlist('assignees')

        existing = Project.query.filter_by(code=code).first()
        if existing:
            flash("🚫 동일한 프로젝트 코드가 이미 존재합니다.", "danger")
            return redirect(url_for('project.create_project'))

        project = Project(
            project_name=project_name,
            solution_name=solution_name,
            company=company,
            location=location,
            code=code
        )

        for user_id in assignee_ids:
            user = User.query.get(int(user_id))
            if user:
                project.assignees.append(user)

        db.session.add(project)
        db.session.commit()
        flash("✅ 프로젝트가 성공적으로 등록되었습니다.", "success")
        return redirect(url_for('dashboard.dashboard'))

    return render_template('create_project.html', users=all_users)
