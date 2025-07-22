from . import db
from datetime import datetime

# --- Association Table for ProjectUpdate Assignees ---

project_update_assignees = db.Table(
    'project_update_assignees',
    db.Column('project_update_id', db.Integer, db.ForeignKey('project_update.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# --- Models ---

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    reports = db.relationship('Report', back_populates='user', cascade='all, delete-orphan')
    assigned_project_updates = db.relationship(
        'ProjectUpdate',
        secondary=project_update_assignees,
        back_populates='assignees'
    )


class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False, index=True)
    week_end = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Draft', 'Submitted', name='report_status'), default='Draft')
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='reports')
    other_notes_entries = db.relationship('OtherNote', back_populates='report', cascade='all, delete-orphan')
    personal_schedules = db.relationship('PersonalSchedule', back_populates='report', cascade='all, delete-orphan')
    solution_items = db.relationship('SolutionItem', back_populates='report', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'week_start', name='uix_user_week_start'),
    )


class OtherNote(db.Model):
    __tablename__ = 'other_note'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', back_populates='other_notes_entries')


class PersonalSchedule(db.Model):
    __tablename__ = 'personal_schedule'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    category = db.Column(
        db.Enum('출장', '외근', '휴가', '휴일근무', name='schedule_category'),
        nullable=False
    )
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    report = db.relationship('Report', back_populates='personal_schedules')
    companions = db.relationship('Companion', back_populates='personal_schedule', cascade='all, delete-orphan')


class Companion(db.Model):
    __tablename__ = 'companion'

    id = db.Column(db.Integer, primary_key=True)
    personal_schedule_id = db.Column(db.Integer, db.ForeignKey('personal_schedule.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    personal_schedule = db.relationship('PersonalSchedule', back_populates='companions')


class SolutionItem(db.Model):
    __tablename__ = 'solution_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))

    report = db.relationship('Report', back_populates='solution_items')
    projects = db.relationship('Project', back_populates='solution_item', cascade='all, delete-orphan')
    sales_supports = db.relationship('SalesSupport', back_populates='solution_item', cascade='all, delete-orphan')


class Project(db.Model):
    __tablename__ = 'project'
    #add revision version
    id = db.Column(db.Integer, primary_key=True)
    solution_item_id = db.Column(db.Integer, db.ForeignKey('solution_item.id'), nullable=False)
    solution_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    solution_item = db.relationship('SolutionItem', back_populates='projects')
    project_updates = db.relationship('ProjectUpdate', back_populates='project', cascade='all, delete-orphan')
    


class ProjectUpdate(db.Model):
    __tablename__ = 'project_update'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    progress = db.Column(db.Text, nullable=False)
    issue = db.Column(db.Text)
    sales_support = db.Column(db.Text)
    other_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship('Project', back_populates='project_updates')
    assignees = db.relationship(
        'User',
        secondary=project_update_assignees,
        back_populates='assigned_project_updates'
    )


class SalesSupport(db.Model):
    __tablename__ = 'sales_support'

    id = db.Column(db.Integer, primary_key=True)
    solution_item_id = db.Column(db.Integer, db.ForeignKey('solution_item.id'), nullable=False)
    system = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    schedule = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    companion = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    solution_item = db.relationship('SolutionItem', back_populates='sales_supports')
    companions = db.relationship('SalesSupportCompanion', back_populates='sales_support', cascade='all, delete-orphan')


class SalesSupportCompanion(db.Model):
    __tablename__ = 'sales_support_companion'

    id = db.Column(db.Integer, primary_key=True)
    sales_support_id = db.Column(db.Integer, db.ForeignKey('sales_support.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    sales_support = db.relationship('SalesSupport', back_populates='companions')
