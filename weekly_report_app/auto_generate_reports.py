from app import create_app, db
from app.models import User, Report
from datetime import datetime, timedelta

app = create_app()
app.app_context().push()

today = datetime.today()
start = today - timedelta(days=today.weekday())
end = start + timedelta(days=6)

for user in User.query.filter_by(is_active=True):
    exists = Report.query.filter_by(user_id=user.id, week_start=start).first()
    if not exists:
        report = Report(user_id=user.id, week_start=start, week_end=end)
        db.session.add(report)

db.session.commit()
