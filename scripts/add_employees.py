import os
import sys

# Add app root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db, User  # ✅ import db from models

# Your employee data
employee_data = [
    ("양우성", "30004679", "차장", "woosung.yang@yokogawa.com"),
    ("김정년", "30036413", "대리", "jeongnyeon.kim@yokogawa.com"),
    ("김민욱", "30040640", "차장", "minwook.kim@yokogawa.com"),
    ("노덕기", "30041568", "차장", "duckgee.noh@yokogawa.com"),
    ("유세훈", "30046341", "과장", "sehun.yu@yokogawa.com"),
    ("김강년", "30049038", "대리", "khangnyon.kim@yokogawa.com"),
    ("황태경", "30053653", "대리", "taegyeong.hwang@yokogawa.com"),
    ("김정은", "30056725", "대리", "jeongeun.kim@yokogawa.com"),
    ("민준홍", "30057537", "차장", "joonhong.min@yokogawa.com"),
    ("유혜빈", "30059497", "사원", "hyebin.yoo@yokogawa.com"),
    ("오윤석", "35001480", "대리", "yoonseok.oh@yokogawa.com"),
    ("박현민", "35003195", "대리", "hyunmin.park@yokogawa.com"),
]

def add_employees():
    app = create_app()
    with app.app_context():
        for name, eid, position, email in employee_data:
            if not User.query.filter_by(employee_id=eid).first():
                user = User(name=name, employee_id=eid, position=position, email=email)
                db.session.add(user)
        db.session.commit()
        print("✅ Employees added successfully.")

if __name__ == '__main__':
    add_employees()
