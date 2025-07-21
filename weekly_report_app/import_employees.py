from app import create_app, db
from app.models import User

app = create_app()

# List of employees
employees = [
    {"name": "양우성", "employee_id": "30004679", "position": "차장", "email": "woosung.yang@yokogawa.com"},
    {"name": "김정년", "employee_id": "30036413", "position": "대리", "email": "jeongnyeon.kim@yokogawa.com"},
    {"name": "김민욱", "employee_id": "30040640", "position": "차장", "email": "minwook.kim@yokogawa.com"},
    {"name": "노덕기", "employee_id": "30041568", "position": "차장", "email": "duckgee.noh@yokogawa.com"},
    {"name": "유세훈", "employee_id": "30046341", "position": "과장", "email": "sehun.yu@yokogawa.com"},
    {"name": "김강년", "employee_id": "30049038", "position": "대리", "email": "khangnyon.kim@yokogawa.com"},
    {"name": "황태경", "employee_id": "30053653", "position": "대리", "email": "taegyeong.hwang@yokogawa.com"},
    {"name": "김정은", "employee_id": "30056725", "position": "대리", "email": "jeongeun.kim@yokogawa.com"},
    {"name": "민준홍", "employee_id": "30057537", "position": "차장", "email": "joonhong.min@yokogawa.com"},
    {"name": "유혜빈", "employee_id": "30059497", "position": "사원", "email": "hyebin.yoo@yokogawa.com"},
    {"name": "오윤석", "employee_id": "35001480", "position": "대리", "email": "yoonseok.oh@yokogawa.com"},
    {"name": "박현민", "employee_id": "35003195", "position": "대리", "email": "hyunmin.park@yokogawa.com"},
    {"name": "admin", "employee_id": "0", "position": "admin", "email": "khangnyon.kim@yokogawa.com"}
]

# Insert into database
with app.app_context():
    for emp in employees:
        # Avoid duplicate insertion
        if not User.query.filter_by(employee_id=emp["employee_id"]).first():
            user = User(**emp)
            db.session.add(user)
    db.session.commit()
    print("✅ All employees imported.")
