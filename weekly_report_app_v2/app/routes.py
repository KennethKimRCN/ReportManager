from flask import Blueprint, render_template, jsonify, json, request, redirect, url_for, flash, session, abort
from .models import *
from . import db
from functools import wraps

main = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash("Please log in first.", "error")
            return redirect(url_for('main.login'))
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def home():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')

        user = User.query.filter_by(employee_id=employee_id).first()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid employee ID', 'error')
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')

    if not user_id:
        flash('Please log in first.', 'error')
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.login'))

    all_users = None
    solution_items = None
    all_reports = None
    projects = None
    project_updates = None

    if user.is_admin:
        all_users = User.query.all()
        solution_items = SolutionItem.query.all()
        all_reports = Report.query.join(User).add_columns(
            Report.id, User.employee_id, User.name, Report.week_start,
            Report.week_end, Report.status, Report.submitted_at
        ).all()
        projects = Project.query.options(
            db.joinedload(Project.solution_item),
            db.joinedload(Project.default_assignees)
        ).all()
        project_updates = ProjectUpdate.query.options(
            db.joinedload(ProjectUpdate.project),
            db.joinedload(ProjectUpdate.assignees)
        ).all()

    return render_template(
        'dashboard.html',
        user=user,
        all_users=all_users,
        solution_items=solution_items,
        all_reports=all_reports,
        projects=projects,
        project_updates=project_updates
    )

@main.route('/solution-items/add', methods=['GET', 'POST'])
@admin_required
def add_solution_item():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            flash("Name is required.", "error")
            return redirect(url_for('main.add_solution_item'))

        existing = SolutionItem.query.filter_by(name=name).first()
        if existing:
            flash("Solution item with this name already exists.", "error")
            return redirect(url_for('main.add_solution_item'))

        new_item = SolutionItem(name=name)
        db.session.add(new_item)
        db.session.commit()
        flash("Solution item added successfully.", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('add_solution_item.html')

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash("Please log in first.", "error")
            return redirect(url_for('main.login'))
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            abort(403)  # Forbidden page
        return f(*args, **kwargs)
    return decorated_function

@main.route('/manage-users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main.route('/manage-users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        name = request.form.get('name')
        position = request.form.get('position')
        email = request.form.get('email')
        is_manager = bool(request.form.get('is_manager'))
        is_active = bool(request.form.get('is_active'))
        is_admin = bool(request.form.get('is_admin'))

        if User.query.filter_by(employee_id=employee_id).first():
            flash("Employee ID already exists.", "error")
            return redirect(url_for('main.add_user'))

        new_user = User(
            employee_id=employee_id,
            name=name,
            position=position,
            email=email,
            is_manager=is_manager,
            is_active=is_active,
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        flash("User added successfully.", "success")
        return redirect(url_for('main.manage_users'))

    return render_template('add_edit_user.html', action="Add", user=None)

@main.route('/manage-users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user_to_edit = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user_to_edit.employee_id = request.form.get('employee_id')
        user_to_edit.name = request.form.get('name')
        user_to_edit.position = request.form.get('position')
        user_to_edit.email = request.form.get('email')
        user_to_edit.is_manager = bool(request.form.get('is_manager'))
        user_to_edit.is_active = bool(request.form.get('is_active'))
        user_to_edit.is_admin = bool(request.form.get('is_admin'))

        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for('main.manage_users'))

    return render_template('add_edit_user.html', action="Edit", user=user_to_edit)

@main.route('/reports/edit/<int:report_id>', methods=['GET', 'POST'])
@admin_required
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    # Convert all solutions and their projects to JSON-serializable structure
    all_solutions = []
    for sol in SolutionItem.query.all():
        all_solutions.append({
            'id': sol.id,
            'name': sol.name,
            'projects': [{
                'id': p.id,
                'code': p.code,
                'company': p.company,
                'location': p.location,
                'project_name': p.project_name
            } for p in sol.projects]
        })

    if request.method == 'POST':
        payload = json.loads(request.form.get('data_json'))
        status = payload.get('status')

        report.status = status
        report.submitted_at = datetime.utcnow() if status == 'Submitted' else None

        # --- Clear existing updates ---
        ProjectUpdate.query.filter_by(report_id=report.id).delete()

        # --- Track updated solutions ---
        selected_solution_ids = set()

        for solution_data in payload.get('solutions', []):
            sol_id = solution_data['id']
            selected_solution_ids.add(sol_id)

            solution = SolutionItem.query.get(sol_id)
            if solution and solution not in report.solution_items:
                report.solution_items.append(solution)

            for proj_data in solution_data['projects']:
                update = ProjectUpdate(
                    report=report,
                    project_id=proj_data['id'],
                    schedule=proj_data.get('schedule'),
                    progress=proj_data.get('progress'),
                    issue=proj_data.get('issue')
                )
                db.session.add(update)

        # Remove deselected solution items
        report.solution_items = [
            s for s in report.solution_items if s.id in selected_solution_ids
        ]

        db.session.commit()
        flash("Report saved successfully.", "success")
        return redirect(url_for('main.dashboard'))

    # ---------- Build Initial Data to Pass to Template ----------
    existing_updates = ProjectUpdate.query.filter_by(report_id=report.id).all()
    structured_data = {}

    for update in existing_updates:
        sol = update.project.solution_item
        if sol.id not in structured_data:
            structured_data[sol.id] = {
                'id': sol.id,
                'name': sol.name,
                'projects': []
            }
        structured_data[sol.id]['projects'].append({
            'id': update.project.id,
            'company': update.project.company,
            'location': update.project.location,
            'project_name': update.project.project_name,
            'code': update.project.code,
            'schedule': update.schedule,
            'progress': update.progress,
            'issue': update.issue,
            'assignees': [u.name for u in update.assignees]
        })

    return render_template(
        'edit_report.html',
        report=report,
        all_solutions=all_solutions,
        prefill_data=list(structured_data.values()),
        report_data=list(structured_data.values())  # <-- add this line
    )


@main.route('/solution_items/available')
def get_available_solutions():
    report_id = request.args.get('report_id', type=int)
    report = Report.query.get(report_id)
    used_ids = [s.id for s in report.solution_items]
    available = SolutionItem.query.filter(~SolutionItem.id.in_(used_ids)).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in available])

@main.route('/projects/by_solution/<int:solution_id>')
def get_projects_by_solution(solution_id):
    projects = Project.query.filter_by(solution_item_id=solution_id).all()
    # --- Include default assignees in project API response ---
    return jsonify([{
        'id': p.id,
        'company': p.company,
        'location': p.location,
        'project_name': p.project_name,
        'code': p.code,
        'assignees': [u.name for u in p.default_assignees]
    } for p in projects])
