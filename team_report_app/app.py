from flask import Flask, render_template, request, redirect, session, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, Update
from export import generate_word

app = Flask(__name__)
app.secret_key = 'replace_this_with_a_random_secret_key'

os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)
db_path = os.path.join(app.root_path, 'instance', 'updates.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

EMPLOYEES = {
    "30004679": {"name": "양 우 성", "position": "차장"},
    "30036413": {"name": "김 정 년", "position": "대리"},
    "30040640": {"name": "김 민 욱", "position": "차장"},
    "30041568": {"name": "노 덕 기", "position": "차장"},
    "30046341": {"name": "유 세 훈", "position": "과장"},
    "30049038": {"name": "김 강 년", "position": "대리"},
    "30053653": {"name": "황 태 경", "position": "대리"},
    "30056725": {"name": "김 정 은", "position": "대리"},
    "30057537": {"name": "민 준 홍", "position": "차장"},
    "30059497": {"name": "유 혜 빈", "position": "사원"},
    "35001480": {"name": "오 윤 석", "position": "대리"},
    "35003195": {"name": "박현민", "position": "대리"},
}


def generate_week_options():
    return [f"Y25W{str(i).zfill(2)}" for i in range(20, 41)]


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        emp_id = request.form.get('employee_id', '').strip()
        if emp_id in EMPLOYEES:
            session['user_id'] = emp_id
            session['name'] = EMPLOYEES[emp_id]['name']
            session['position'] = EMPLOYEES[emp_id]['position']
            return redirect('/dashboard')
        else:
            error = "유효하지 않은 사번입니다. 다시 입력해주세요."
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    query = request.args.get('query', '').strip()
    if query:
        updates = Update.query.filter(
            (Update.name.contains(query)) |
            (Update.week.contains(query))
        ).order_by(Update.week.desc()).all()
    else:
        updates = Update.query.order_by(Update.week.desc()).all()

    return render_template('dashboard.html', updates=updates)


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'user_id' not in session:
        return redirect('/login')

    week_options = generate_week_options()

    if request.method == 'POST':
        update = Update(
            name=session.get('name'),
            position=session.get('position'),
            week=request.form.get('week', ''),

            project_summary=request.form.get('project_summary', ''),
            milestones=request.form.get('milestones', ''),
            progress=request.form.get('progress', ''),
            project_issues=request.form.get('project_issues', ''),
            sales_support=request.form.get('sales_support', ''),
            other_notes=request.form.get('other_notes', ''),
            business_trip=request.form.get('business_trip', ''),
            external_work=request.form.get('external_work', ''),
            vacation=request.form.get('vacation', ''),
            weekend_work=request.form.get('weekend_work', ''),
        )
        db.session.add(update)
        db.session.commit()
        return redirect('/dashboard')

    return render_template(
        'submit.html',
        name=session.get('name', ''),
        position=session.get('position', ''),
        week_options=week_options
    )


@app.route('/report/<int:report_id>')
def report_detail(report_id):
    if 'user_id' not in session:
        return redirect('/login')
    update = Update.query.get_or_404(report_id)
    return render_template('report_detail.html', update=update)


@app.route('/report')
def report():
    if 'user_id' not in session:
        return redirect('/login')
    updates = Update.query.order_by(Update.id.desc()).all()
    return render_template('report.html', updates=updates)


@app.route('/export/word/<int:report_id>')
def export_single_word(report_id):
    if 'user_id' not in session:
        return redirect('/login')
    update = Update.query.get_or_404(report_id)
    filepath = generate_word(single_report=update)
    return send_file(filepath, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
