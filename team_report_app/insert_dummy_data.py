from models import db, User
from user_data import users
from app import app

with app.app_context():
    for employee_id, info in users.items():
        existing_user = User.query.filter_by(employee_id=employee_id).first()
        if not existing_user:
            user = User(
                employee_id=employee_id,
                name=info['name'],
                position=info['position']
            )
            db.session.add(user)
    db.session.commit()
    print("User data inserted/updated.")
