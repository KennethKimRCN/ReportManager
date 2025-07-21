from flask import Flask, render_template, request, redirect, session, jsonify
from models import db, User, Project

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db.init_app(app)

with app.app_context():
    db.create_all()
    if not Project.query.first():
        db.session.add(Project(schedule="", progress="", other_notes=""))
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User.query.filter_by(id=user_id).first()
        if user:
            session['user_id'] = user.id
            return redirect('/editor')
        else:
            return "Invalid ID"
    return render_template('login.html')

@app.route('/editor')
def editor():
    if 'user_id' not in session:
        return redirect('/')
    project = Project.query.first()
    return render_template('editor.html', project=project)

@app.route('/update', methods=['POST'])
def update():
    field = request.form['field']
    value = request.form['value']
    project = Project.query.first()
    setattr(project, field, value)
    db.session.commit()
    return '', 204

@app.route('/get_project')
def get_project():
    project = Project.query.first()
    return jsonify({
        'schedule': project.schedule,
        'progress': project.progress,
        'other_notes': project.other_notes
    })

if __name__ == '__main__':
    app.run(debug=True)
