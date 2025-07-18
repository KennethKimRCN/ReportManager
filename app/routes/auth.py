from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        user = User.query.filter_by(employee_id=employee_id).first()
        if user:
            session['user_id'] = user.id
            session['name'] = user.name
            session['position'] = user.position
            session['employee_id'] = user.employee_id
            flash(f"{user.name}님 환영합니다!", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("등록되지 않은 사번입니다.", "danger")
    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", "info")
    return redirect(url_for('auth.login'))
