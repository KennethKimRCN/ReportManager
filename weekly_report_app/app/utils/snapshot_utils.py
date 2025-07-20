from app.models import ProjectSnapshot, Project
from app.utils.date_utils import get_current_week_range
from app import db


def ensure_snapshot_for_project(project_id):
    week_start, _ = get_current_week_range()
    existing = ProjectSnapshot.query.filter_by(project_id=project_id, week_start=week_start).first()
    if existing:
        return

    project = Project.query.get(project_id)
    snapshot = ProjectSnapshot(
        project_id=project.id,
        week_start=week_start,
        solution_name=project.solution_name,
        company=project.company,
        location=project.location,
        project_name=project.project_name,
        code=project.code,
        status=project.status
    )
    db.session.add(snapshot)
    db.session.commit()
