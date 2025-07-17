from flask import Flask, render_template, request, redirect, send_file
from models import db, Update
from export import generate_word, generate_pdf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///updates.db'
db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        update = Update(
            name=request.form['name'],
            project=request.form['project'],
            update=request.form['update']
        )
        db.session.add(update)
        db.session.commit()
        return redirect('/report')
    return render_template('submit.html')

@app.route('/report')
def report():
    updates = Update.query.all()
    return render_template('report.html', updates=updates)

@app.route('/export/word')
def export_word():
    filepath = generate_word()
    return send_file(filepath, as_attachment=True)

@app.route('/export/pdf')
def export_pdf():
    filepath = generate_pdf()
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
