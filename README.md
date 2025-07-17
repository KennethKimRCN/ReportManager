# Team Weekly Report Manager

A simple Flask-based web application designed to streamline weekly report submissions, avoid email chaos, and auto-generate reports in Word format — all while keeping a familiar structure your micromanaging boss loves.

---

## 🧩 Features

- 🔐 **Login by Employee ID (글로벌 사번)** — Autofill name and position (직급)
- 📝 **Submit Weekly Reports** — Form replicates your boss's rigid format
- 📅 **Dashboard** — See all reports in card format (filter by Y25Wxx)
- 👀 **View Reports** — Click a report card to see full details
- ✏️ **Edit & Delete Reports** — Update or remove previously submitted reports
- 📤 **Export to Word** — Boss gets a compiled Word file in the format he loves

---

## 🚀 How to Run

### 1. Clone this Repository
```
git clone https://github.com/yourname/team-report-app.git
cd team-report-app
```

### 2. Create Virtual Environment
```
python -m venv venv
.env\Scriptsctivate
```

### 3. Install Requirements
```
pip install -r requirements.txt
```

### 4. Set Up the Database
```python
# In Python shell or a script
from app import app
from models import db
with app.app_context():
    db.create_all()
```

### 5. Run the App
```
python app.py
```

Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 📁 Project Structure

```
team_report_app/
├── app.py                 # Main Flask app
├── models.py              # SQLAlchemy models
├── templates/
│   ├── dashboard.html     # Report dashboard
│   ├── submit.html        # Report submission form
│   ├── report_detail.html # Report detail view
│   └── edit_report.html   # Report edit form
├── static/
│   └── style.css          # Optional CSS styles
├── instance/
│   └── updates.db         # SQLite database
├── venv/                  # Python virtual environment
├── requirements.txt
└── README.md              # This file
```

---

## 📦 Dependencies

- Flask
- Flask_SQLAlchemy
- python-docx

Install them via:
```
pip install Flask Flask_SQLAlchemy python-docx
```

---

## 📄 Export Format

The exported Word document follows this structure per report:

```
[주간보고] XXX 차장 – W28

▶ 프로젝트 특이사항
...내용...

▶ Key Milestone
...내용...

▶ 진행상황
...내용...

▶ 특이사항
...내용...

▶ 영업지원 사항
...내용...

▶ 그 외 특이사항
...내용...

▶ 개인 일정
출장: ...내용...
외근: ...내용...
휴가: ...내용...
휴일근무: ...내용...
```

---

## ✍️ Author

Built with ❤️ by your overworked team member.