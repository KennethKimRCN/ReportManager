from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    employee_id = db.Column(db.String(20))  # ← Add this line
    position = db.Column(db.String(20))
    week = db.Column(db.String(10))
    project_summary = db.Column(db.Text)
    milestones = db.Column(db.Text)
    progress = db.Column(db.Text)
    project_issues = db.Column(db.Text)
    sales_support = db.Column(db.Text)
    other_notes = db.Column(db.Text)
    business_trip = db.Column(db.Text)
    external_work = db.Column(db.Text)
    vacation = db.Column(db.Text)
    weekend_work = db.Column(db.Text)
