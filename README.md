
# 📝 Team Weekly Report Management System

A web-based platform to manage weekly team activity reports with project-based context. Built with Flask and SQLite, it supports multiple users, project assignments, secure login, report submission, and exports.

---

## 🔧 Features

- 🔐 **Login System** using employee ID
- 🗃️ **Project Registration** (Solution Name, Company, Location, Code)
- 📤 **Weekly Report Submission** with multi-project selection
- 📊 **Dashboard View** for all reports with project/user context
- 🔍 **Detailed Report View** per submission
- ✏️ **Edit & Delete** own reports
- 📁 **Export Report to Word (.docx)**
- 🧾 **Admin Page** listing all Users, Projects, and Reports

---

## 🗂️ Project Structure

```
team_report_app/
│
├── app.py                  # Main Flask app logic
├── models.py               # SQLAlchemy database models
├── user_data.py            # Static dictionary of employee_id to user info
├── /templates              # HTML templates (Jinja2)
│   ├── login.html
│   ├── dashboard.html
│   ├── submit.html
│   ├── create_project.html
│   ├── view_report.html
│   ├── edit_report.html
│   └── admin_data.html
├── /static                 # CSS files (optional)
│   └── style.css
└── /instance/updates.db    # SQLite DB file
```

---

## 🚀 How to Run (Windows)

1. **Create Virtual Environment**

```bash
python -m venv venv
venv\Scripts\activate
```

2. **Install Requirements** (if you add `requirements.txt`)

```bash
pip install flask flask_sqlalchemy python-docx
```

3. **Run App**

```bash
cd team_report_app
python app.py
```

App will run at: `http://localhost:5000`

---

## 🧠 Developer Notes

- Login is handled via `session['employee_id']`, validated against `User` table.
- `user_data.py` contains predefined employee info. Run a one-time script to load them.
- Projects must be registered before reports can be submitted.
- Users can select multiple projects and submit a report per project.
- Each report is tied to a `User`, `Project`, and `Week` (`Y25W##` format).
- Admin page `/admin/data` lists all Users, Projects, and Updates.

---

## 📥 Useful Snippets

**Register users from user_data.py**:

```python
from models import db, User
from app import app
from user_data import users

with app.app_context():
    for eid, info in users.items():
        if not User.query.filter_by(employee_id=eid).first():
            db.session.add(User(employee_id=eid, name=info['name'], position=info['position']))
    db.session.commit()
```

---

## 🧾 Future Improvements

- Role-based access (admin vs normal users)
- Search/filter by project, week, or user
- PDF export (currently Word only)
- Better UI (modals for project creation, validation)

---

## 👤 Author

- Internal tool for efficient team report management
- Designed by [Your Name or Team]
