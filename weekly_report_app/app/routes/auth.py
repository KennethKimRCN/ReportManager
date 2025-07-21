from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app.models import User
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        user = User.query.filter_by(employee_id=employee_id).first()

        if user:
            session['user_id'] = user.id
            session['is_manager'] = user.is_manager
            session['user_name'] = user.name
            session['employee_id'] = user.employee_id
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid Employee ID')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
