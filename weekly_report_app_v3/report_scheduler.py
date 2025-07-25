from datetime import datetime
from pytz import timezone
from app import db  # replace with your actual app import
from app.models import User, Report  # adjust import paths as needed

# Set timezone to Korea Standard Time (KST)
kst = timezone('Asia/Seoul')

def generate_weekly_reports():
    now = datetime.now(kst)
    iso_year, iso_week, _ = now.isocalendar()

    # Get all active users only
    active_users = User.query.filter_by(is_active=True).all()

    created_count = 0
    skipped_count = 0

    for user in active_users:
        # Check if report already exists for this user, year, and week
        existing = Report.query.filter_by(
            user_id=user.id,
            year=iso_year,
            week=iso_week
        ).first()

        if existing:
            skipped_count += 1
            continue

        # Create new draft report for the user
        new_report = Report(
            user_id=user.id,
            year=iso_year,
            week=iso_week,
            status='Draft'
        )
        db.session.add(new_report)
        created_count += 1

    # Commit all new reports to DB
    db.session.commit()

    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Reports created: {created_count}, Skipped: {skipped_count}")

# Example: APScheduler setup
if __name__ == "__main__":
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler(timezone=kst)
    # Schedule job to run every Sunday at 00:00 KST
    scheduler.add_job(generate_weekly_reports, 'cron', day_of_week='sun', hour=0, minute=0)
    scheduler.start()

    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        import time
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")
