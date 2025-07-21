from datetime import timedelta
from app.models import User, Report
from app import db
from app.utils.date_utils import get_sunday_of_current_week

def generate_weekly_reports_if_missing():
    week_start = get_sunday_of_current_week()
    week_end = week_start + timedelta(days=6)

    employees = User.query.filter_by(is_manager=False).all()

    for user in employees:
        exists = Report.query.filter_by(user_id=user.id, week_start=week_start).first()
        if not exists:
            report = Report(
                user_id=user.id,
                week_start=week_start,
                week_end=week_end,
                status='Draft'
            )
            db.session.add(report)

    db.session.commit()
