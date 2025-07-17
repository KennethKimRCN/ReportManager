from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for Project ↔ User (many-to-many)
project_assignees = db.Table('project_assignees',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(20), nullable=False)

    updates = db.relationship('Update', backref='user', lazy=True)
    assigned_projects = db.relationship(
        'Project',
        secondary=project_assignees,
        back_populates='assignees'
    )

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    solution_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    company = db.Column(db.String(100))
    project_name = db.Column(db.String(100))
    code = db.Column(db.String(50))
    progress = db.Column(db.Text)      # 진행상황
    issues = db.Column(db.Text)        # 특이사항

    assignees = db.relationship(
        'User',
        secondary=project_assignees,
        back_populates='assigned_projects'
    )

    updates = db.relationship('Update', backref='project', lazy=True)

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    week = db.Column(db.String(10))
    progress = db.Column(db.Text)
    project_issues = db.Column(db.Text)
    sales_support = db.Column(db.Text)  # legacy, optional
    other_notes = db.Column(db.Text)    # legacy, optional
    business_trip = db.Column(db.Text)  # legacy, optional
    external_work = db.Column(db.Text)  # legacy, optional
    vacation = db.Column(db.Text)       # legacy, optional
    weekend_work = db.Column(db.Text)   # legacy, optional

    sales_supports = db.relationship('SalesSupport', backref='update', cascade="all, delete-orphan")
    other_notes_entries = db.relationship('OtherNote', backref='update', cascade="all, delete-orphan")
    personal_schedules = db.relationship('PersonalSchedule', backref='update', cascade="all, delete-orphan")

class SalesSupport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    update_id = db.Column(db.Integer, db.ForeignKey('update.id'), nullable=False)
    system = db.Column(db.String(100))     # 시스템 (ex MPA)
    company = db.Column(db.String(100))    # 업체
    schedule = db.Column(db.String(100))   # 일정
    content = db.Column(db.Text)           # 지원내용
    companion = db.Column(db.String(100))  # 동행자

class OtherNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    update_id = db.Column(db.Integer, db.ForeignKey('update.id'), nullable=False)
    note = db.Column(db.Text)  # 예: 세미나 지원, 장기교육 등

class PersonalSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    update_id = db.Column(db.Integer, db.ForeignKey('update.id'), nullable=False)
    category = db.Column(db.String(20))      # 출장, 외근, 휴가, 휴일근무
    person = db.Column(db.String(100))       # xxx 사원
    location = db.Column(db.String(100))     # 장소 (e.g., 여수)
    start_date = db.Column(db.String(20))    # 시작일
    end_date = db.Column(db.String(20))      # 종료일
    description = db.Column(db.Text)         # 비고 내용 (e.g., ST-UP)
