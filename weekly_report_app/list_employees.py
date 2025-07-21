from app import create_app, db
from app.models import User
from tabulate import tabulate

app = create_app()

with app.app_context():
    employees = User.query.order_by(User.position, User.name).all()

    if not employees:
        print("❌ No employees found in the database.")
    else:
        table = [
            [emp.name, emp.employee_id, emp.position, emp.email, emp.is_manager]
            for emp in employees
        ]
        headers = ["Name", "Employee ID", "Position", "Email", "Is Manager"]
        print(tabulate(table, headers=headers, tablefmt="grid"))
