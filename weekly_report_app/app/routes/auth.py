from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user
from .models import User
from . import db, login_manager

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form['employee_id'].strip()
        user = User.query.filter_by(employee_id=employee_id).first()
        if user:
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid employee ID')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
