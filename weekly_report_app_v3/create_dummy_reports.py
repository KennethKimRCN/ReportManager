# create_reports.py

from datetime import date, timedelta
from app import create_app, db
from app.models import User, Report

def create_empty_reports_for_this_and_last_week():
    app = create_app()
    with app.app_context():
        today = date.today()

        # Get ISO week numbers for this week and last week
        this_year, this_week, _ = today.isocalendar()
        last_week_date = today - timedelta(weeks=1)
        last_year, last_week, _ = last_week_date.isocalendar()

        week_pairs = [
            (last_year, last_week),
            (this_year, this_week)
        ]

        users = User.query.all()

        for user in users:
            for year, week in week_pairs:
                # Check if report already exists (based on user_id, year, week)
                existing_report = Report.query.filter_by(user_id=user.id, year=year, week=week).first()
                if not existing_report:
                    report = Report(
                        user_id=user.id,
                        year=year,
                        week=week,
                        status='Draft'
                    )
                    db.session.add(report)
                    print(f"Created report for user {user.employee_id} for year {year} week {week}")

        try:
            db.session.commit()
            print("Done creating reports.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to commit: {e}")

if __name__ == "__main__":
    create_empty_reports_for_this_and_last_week()
