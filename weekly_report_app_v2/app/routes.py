from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
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
    all_reports = None  # Add this

    if user.is_admin:
        all_users = User.query.all()
        solution_items = SolutionItem.query.all()
        all_reports = Report.query.join(User).add_columns(
            Report.id, User.employee_id, User.name, Report.week_start,
            Report.week_end, Report.status, Report.submitted_at
        ).all()

    return render_template('dashboard.html', user=user, all_users=all_users, solution_items=solution_items, all_reports=all_reports)


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

@main.route('/manage-users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User deleted successfully.", "success")
    return redirect(url_for('main.manage_users'))

@main.route('/reports/edit/<int:report_id>', methods=['GET', 'POST'])
@admin_required
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)
    all_solutions = SolutionItem.query.all()

    if request.method == 'POST':
        status = request.form.get('status')

        if status not in ['Draft', 'Submitted']:
            flash('Invalid status selected.', 'error')
            return redirect(url_for('main.edit_report', report_id=report_id))

        # Submission handling
        if status == 'Submitted' and not report.submitted_at:
            report.submitted_at = datetime.utcnow()
        elif status == 'Draft':
            report.submitted_at = None

        report.status = status

        # Handle solution associations
        selected_ids = set(map(int, request.form.getlist('solution_ids[]')))

        for solution in all_solutions:
            if solution.id in selected_ids:
                solution.report = report
            elif solution.report_id == report.id:
                solution.report = None

        db.session.commit()
        flash('Report updated successfully.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_report.html', report=report, all_solutions=all_solutions)