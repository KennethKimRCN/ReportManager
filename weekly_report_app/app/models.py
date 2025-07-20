from . import db
from datetime import datetime, time

# --- Association Tables ---

# Many-to-many between Project and User (assignees)
project_assignees = db.Table(
    'project_assignees',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Many-to-many between Project and Tag
project_tags = db.Table(
    'project_tags',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('project_tag.id'))
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

    assigned_projects = db.relationship(
        'Project', secondary=project_assignees, back_populates='assignees'
    )
    reports = db.relationship(
        'Report', back_populates='user', cascade='all, delete-orphan'
    )
    edits = db.relationship('EditLog', back_populates='user')


class ProjectTag(db.Model):
    __tablename__ = 'project_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    solution_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(
        db.Enum('Pre-Sales', 'Ongoing', 'Maintenance', 'Completed', name='project_status'),
        default='Ongoing'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignees = db.relationship(
        'User', secondary=project_assignees, back_populates='assigned_projects'
    )
    tags = db.relationship(
        'ProjectTag', secondary=project_tags, backref='projects'
    )
    snapshots = db.relationship('ProjectSnapshot', back_populates='project', cascade='all, delete-orphan')
    sales_supports = db.relationship('SalesSupport', backref='project')
    change_logs = db.relationship('ProjectChangeLog', back_populates='project', cascade='all, delete-orphan')
    project_updates = db.relationship('ProjectUpdate', back_populates='project')


class ProjectSnapshot(db.Model):
    __tablename__ = 'project_snapshot'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False, index=True)
    solution_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', back_populates='snapshots')

    __table_args__ = (
        db.UniqueConstraint('project_id', 'week_start', name='uix_snapshot_per_week'),
    )


class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    week_start = db.Column(db.Date, nullable=False, index=True)  # Sunday
    week_end = db.Column(db.Date, nullable=False)                # Saturday
    status = db.Column(
        db.Enum('Draft', 'Submitted', name='report_status'),
        default='Draft'
    )
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='reports')
    sales_supports = db.relationship('SalesSupport', back_populates='report', cascade='all, delete-orphan')
    other_notes_entries = db.relationship('OtherNote', back_populates='report', cascade='all, delete-orphan')
    personal_schedules = db.relationship('PersonalSchedule', back_populates='report', cascade='all, delete-orphan')
    project_change_logs = db.relationship('ProjectChangeLog', back_populates='report', cascade='all, delete-orphan')
    project_updates = db.relationship('ProjectUpdate', back_populates='report', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'week_start', name='uix_user_week_start'),
    )


class ProjectUpdate(db.Model):
    __tablename__ = 'project_update'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    progress = db.Column(db.Text, nullable=False)
    issue = db.Column(db.Text)
    sales_support = db.Column(db.Text)
    other_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', back_populates='project_updates')
    project = db.relationship('Project', back_populates='project_updates')

    __table_args__ = (
        db.UniqueConstraint('report_id', 'project_id', name='uix_report_project'),
    )


class SalesSupport(db.Model):
    __tablename__ = 'sales_support'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    system = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    schedule = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    companion = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', back_populates='sales_supports')


class OtherNote(db.Model):
    __tablename__ = 'other_note'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    note = db.Column(db.Text, nullable=False)
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
    person = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', back_populates='personal_schedules')


class ProjectChangeLog(db.Model):
    __tablename__ = 'project_change_log'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    change_summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship('Project', back_populates='change_logs')
    report = db.relationship('Report', back_populates='project_change_logs')


class EditLog(db.Model):
    __tablename__ = 'edit_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    object_id = db.Column(db.Integer, nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='edits')
