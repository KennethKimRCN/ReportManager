from . import db
from datetime import datetime

# --- Association Table for ProjectUpdate Assignees ---

project_update_assignees = db.Table(
    'project_update_assignees',
    db.Column('project_update_id', db.Integer, db.ForeignKey('project_update.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Default assignees per Project (template-level)
project_assignees = db.Table(
    'project_assignees',
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Many-to-many: Report <-> SolutionItem
report_solution_items = db.Table(
    'report_solution_items',
    db.Column('report_id', db.Integer, db.ForeignKey('report.id'), primary_key=True),
    db.Column('solution_item_id', db.Integer, db.ForeignKey('solution_item.id'), primary_key=True)
)

# --- Models ---

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(10), nullable=False)
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
    assigned_projects = db.relationship(
        'Project',
        secondary=project_assignees,
        back_populates='default_assignees'
    )

## Report Related DB schema
class Report(db.Model):
    __tablename__ = 'report'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    year = db.Column(db.Integer, nullable=False, index=True)
    week = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), nullable=False, default='draft')
    submitted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='reports')

    solution_items = db.relationship(
        'SolutionItem',
        secondary=report_solution_items,
        back_populates='reports'
    )

    project_updates = db.relationship('ProjectUpdate', back_populates='report', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'year', 'week', name='uix_user_year_week'),
    )


class SolutionItem(db.Model):
    __tablename__ = 'solution_item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    issue = db.Column(db.Text)

    reports = db.relationship(
        'Report',
        secondary=report_solution_items,
        back_populates='solution_items'
    )

    projects = db.relationship('Project', back_populates='solution_item')

class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    solution_item_id = db.Column(db.Integer, db.ForeignKey('solution_item.id'), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    solution_item = db.relationship('SolutionItem', back_populates='projects')
    project_updates = db.relationship('ProjectUpdate', back_populates='project', cascade='all, delete-orphan')

    default_assignees = db.relationship(
        'User',
        secondary=project_assignees,
        back_populates='assigned_projects'
    )

class ProjectUpdate(db.Model):
    __tablename__ = 'project_update'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

    schedule = db.Column(db.Text)
    progress = db.Column(db.Text)
    issue = db.Column(db.Text)


    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    report = db.relationship('Report', back_populates='project_updates')
    project = db.relationship('Project', back_populates='project_updates')

    assignees = db.relationship(
        'User',
        secondary=project_update_assignees,
        back_populates='assigned_project_updates'
    )