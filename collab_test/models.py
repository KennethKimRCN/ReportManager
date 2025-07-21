from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    schedule = db.Column(db.Text, default="")
    progress = db.Column(db.Text, default="")
    other_notes = db.Column(db.Text, default="")
