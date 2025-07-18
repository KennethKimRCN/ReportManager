import os
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify
)
from models import db, User, Project, Update, PersonalSchedule
from functools import wraps

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'updates.db')

app = Flask(__name__)
app.secret_key = 'change_this_secret_to_a_random_value'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Login required decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            flash("로그인이 필요합니다.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        user = User.query.filter_by(employee_id=employee_id).first()
        if user:
            session['employee_id'] = user.employee_id
            session['name'] = user.name
            session['position'] = user.position
            return redirect(url_for('dashboard'))
        else:
            flash("존재하지 않는 사번입니다.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    grouped = {}
    all_updates = Update.query.order_by(Update.week.desc()).all()
    for update in all_updates:
        key = (update.user.name, update.user.position, update.week)
        grouped.setdefault(key, []).append(update)
    return render_template('dashboard.html', grouped_reports=grouped)

@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        user = User.query.filter_by(employee_id=session['employee_id']).first()
        week = request.form.get('week')
        project_ids = request.form.getlist('project_ids')

        for pid in project_ids:
            update = Update(
                user_id=user.id,
                project_id=int(pid),
                week=week,
                progress=request.form.get(f'progress_{pid}'),
                project_issues=request.form.get(f'issues_{pid}'),
                sales_support=request.form.get(f'sales_support_{pid}'),
                other_notes=request.form.get(f'other_notes_{pid}')
            )
            db.session.add(update)

        # Add shared schedule
        def create_schedule(category):
            persons = request.form.getlist(f'{category}_person')
            locations = request.form.getlist(f'{category}_location')
            start_dates = request.form.getlist(f'{category}_start')
            end_dates = request.form.getlist(f'{category}_end')
            descriptions = request.form.getlist(f'{category}_desc')
            return zip(persons, locations, start_dates, end_dates, descriptions)

        for category in ['출장', '외근', '휴가', '휴일근무']:
            for person, location, start, end, desc in create_schedule(category):
                schedule = PersonalSchedule(
                    user_id=user.id,
                    week=week,
                    category=category,
                    person=person,
                    location=location,
                    start_date=start,
                    end_date=end,
                    description=desc
                )
                db.session.add(schedule)

        db.session.commit()
        flash("보고서가 제출되었습니다.")
        return redirect(url_for('dashboard'))

    return render_template('submit.html')

@app.route('/projects/new', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        solution_name = request.form['solution_name']
        location = request.form['location']
        company = request.form['company']
        project_name = request.form['project_name']
        code = request.form['code']
        assignee_ids = request.form.getlist('assignees[]')

        project = Project(
            solution_name=solution_name,
            location=location,
            company=company,
            project_name=project_name,
            code=code
        )

        for eid in assignee_ids:
            user = User.query.filter_by(employee_id=eid).first()
            if user:
                project.assignees.append(user)

        db.session.add(project)
        db.session.commit()
        flash("프로젝트가 등록되었습니다.")
        return redirect(url_for('dashboard'))

    return render_template('create_project.html')

@app.route('/project-popup')
@login_required
def project_popup():
    projects = Project.query.all()
    return render_template('project_popup.html', projects=projects)

@app.route('/employees/popup')
@login_required
def employee_popup():
    users = User.query.order_by(User.name).all()  # Make sure User is imported from models
    return render_template('employee_popup.html', users=users)

@app.route('/report/<string:employee_id>/<string:week>')
@login_required
def view_report(employee_id, week):
    user = User.query.filter_by(employee_id=employee_id).first_or_404()
    updates = Update.query.filter_by(user_id=user.id, week=week).all()
    schedules = PersonalSchedule.query.filter_by(user_id=user.id, week=week).all()
    return render_template('view_report.html', updates=updates, schedules=schedules, user=user, week=week)

@app.route('/edit/<string:employee_id>/<string:week>', methods=['GET', 'POST'])
@login_required
def edit_report(employee_id, week):
    user = User.query.filter_by(employee_id=employee_id).first_or_404()
    updates = Update.query.filter_by(user_id=user.id, week=week).all()
    schedules = PersonalSchedule.query.filter_by(user_id=user.id, week=week).all()

    if request.method == 'POST':
        for update in updates:
            pid = str(update.project_id)
            update.progress = request.form.get(f'progress_{pid}')
            update.project_issues = request.form.get(f'issues_{pid}')
            update.sales_support = request.form.get(f'sales_support_{pid}')
            update.other_notes = request.form.get(f'other_notes_{pid}')
        db.session.query(PersonalSchedule).filter_by(user_id=user.id, week=week).delete()

        def create_schedule(category):
            persons = request.form.getlist(f'{category}_person')
            locations = request.form.getlist(f'{category}_location')
            start_dates = request.form.getlist(f'{category}_start')
            end_dates = request.form.getlist(f'{category}_end')
            descriptions = request.form.getlist(f'{category}_desc')
            return zip(persons, locations, start_dates, end_dates, descriptions)

        for category in ['출장', '외근', '휴가', '휴일근무']:
            for person, location, start, end, desc in create_schedule(category):
                schedule = PersonalSchedule(
                    user_id=user.id,
                    week=week,
                    category=category,
                    person=person,
                    location=location,
                    start_date=start,
                    end_date=end,
                    description=desc
                )
                db.session.add(schedule)

        db.session.commit()
        flash("보고서가 수정되었습니다.")
        return redirect(url_for('view_report', employee_id=employee_id, week=week))

    return render_template('edit_report.html', updates=updates, schedules=schedules, user=user, week=week)

@app.route('/delete/<string:employee_id>/<string:week>', methods=['POST'])
@login_required
def delete_report(employee_id, week):
    user = User.query.filter_by(employee_id=employee_id).first_or_404()
    Update.query.filter_by(user_id=user.id, week=week).delete()
    PersonalSchedule.query.filter_by(user_id=user.id, week=week).delete()
    db.session.commit()
    flash("보고서가 삭제되었습니다.")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
