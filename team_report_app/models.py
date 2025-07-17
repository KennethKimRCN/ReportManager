from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    project = db.Column(db.String(100), nullable=False)
    update = db.Column(db.Text, nullable=False)
