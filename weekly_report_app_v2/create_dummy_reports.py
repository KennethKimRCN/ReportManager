# create_reports.py

from datetime import date, timedelta
from app import create_app, db
from app.models import User, Report

def create_empty_reports_for_this_and_last_week():
    app = create_app()
    with app.app_context():
        today = date.today()
        # Find Monday of this week
        this_monday = today - timedelta(days=today.weekday())
        last_monday = this_monday - timedelta(weeks=1)

        weeks = [this_monday, last_monday]

        users = User.query.all()

        for user in users:
            for week_start in weeks:
                week_end = week_start + timedelta(days=6)
                # Check if report already exists
                existing_report = Report.query.filter_by(user_id=user.id, week_start=week_start).first()
                if not existing_report:
                    new_report = Report(
                        user_id=user.id,
                        week_start=week_start,
                        week_end=week_end,
                        status='Draft'
                    )
                    db.session.add(new_report)
                    print(f"Created report for user {user.employee_id} for week starting {week_start}")
        db.session.commit()
        print("Done creating reports.")

if __name__ == "__main__":
    create_empty_reports_for_this_and_last_week()
