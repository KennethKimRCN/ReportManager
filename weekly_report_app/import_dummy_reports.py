from app import create_app, db
from app.models import *
from app.utils.date_utils import get_current_week_range
from datetime import datetime, timedelta
import random
from sqlalchemy import text  # <-- Import text here

app = create_app()

def get_week_range(offset_weeks=0):
    # Sunday-based week
    today = datetime.today().date()
    start = today - timedelta(days=today.weekday() + 1 + (7 * offset_weeks))
    end = start + timedelta(days=6)
    return start, end


with app.app_context():
    # === Insert Dummy Manager (if not exists) ===
    manager_email = "manager@yokogawa.com"
    existing_manager = User.query.filter_by(email=manager_email).first()

    if not existing_manager:
        manager = User(
            employee_id="99999999",
            name="관리자",
            position="부장",
            email=manager_email,
            is_manager=True
        )
        db.session.add(manager)
        db.session.commit()
        print("✅ Dummy manager inserted.")
    else:
        print("ℹ️ Dummy manager already exists.")

    # SAFE RESET ONLY FOR PROJECT/REPORT DATA

    # Explicitly clear the association table to avoid UNIQUE constraint error
    db.session.execute(text('DELETE FROM project_assignees'))  # <-- wrap SQL in text()
    db.session.query(ProjectUpdate).delete()
    db.session.query(SalesSupport).delete()
    db.session.query(OtherNote).delete()
    db.session.query(PersonalSchedule).delete()
    db.session.query(ProjectChangeLog).delete()
    db.session.query(ProjectSnapshot).delete()
    db.session.query(Project).delete()
    db.session.query(Report).delete()
    db.session.query(ProjectTag).delete()
    db.session.commit()

    # Load users
    users = User.query.all()
    user_dict = {u.employee_id: u for u in users}

    # Tags
    tag_names = ['DCS', 'MES', 'HMI', 'PLC', 'Dev']
    tags = [ProjectTag(name=name) for name in tag_names]
    db.session.add_all(tags)
    db.session.commit()

    # Dummy Projects
    dummy_projects = [
        {
            "solution_name": "CENTUM VP",
            "company": "ABC Corp",
            "location": "서울",
            "project_name": "서울 스마트팩토리",
            "code": "PRJ001",
            "status": "Ongoing",
            "tag_names": ['DCS', 'MES'],
            "assignee_ids": ['30004679', '30036413']
        },
        {
            "solution_name": "FAST/TOOLS",
            "company": "DEF Co.",
            "location": "부산",
            "project_name": "부산 통합감시",
            "code": "PRJ002",
            "status": "Maintenance",
            "tag_names": ['HMI'],
            "assignee_ids": ['30041568', '30046341']
        },
        {
            "solution_name": "ProSafe-RS",
            "company": "GHI Ltd.",
            "location": "광주",
            "project_name": "광주 화학플랜트",
            "code": "PRJ003",
            "status": "Ongoing",
            "tag_names": ['PLC'],
            "assignee_ids": ['30040640', '30049038']
        }
    ]

    created_projects = []

    for pdata in dummy_projects:
        project = Project(
            solution_name=pdata["solution_name"],
            company=pdata["company"],
            location=pdata["location"],
            project_name=pdata["project_name"],
            code=pdata["code"],
            status=pdata["status"]
        )
        project.tags = [t for t in tags if t.name in pdata["tag_names"]]
        for eid in pdata["assignee_ids"]:
            if eid in user_dict:
                user = user_dict[eid]
                if user not in project.assignees:
                    project.assignees.append(user)

        db.session.add(project)
        created_projects.append(project)

    db.session.commit()

    # Generate data for 4 weeks (0 = current, 1 = 1 week ago, ...)
    for week_offset in range(4):
        week_start, week_end = get_week_range(week_offset)

        for project in created_projects:
            snapshot = ProjectSnapshot(
                project_id=project.id,
                week_start=week_start,
                solution_name=project.solution_name,
                company=project.company,
                location=project.location,
                project_name=project.project_name,
                code=project.code,
                status=project.status
            )
            db.session.add(snapshot)

        for user in users:
            # Only 70% chance of submitting a report for any week
            if random.random() < 0.7:
                report = Report(
                    user_id=user.id,
                    week_start=week_start,
                    week_end=week_end,
                    status='Submitted',
                    submitted_at=datetime.utcnow() - timedelta(days=week_offset*7)
                )
                db.session.add(report)
                db.session.flush()

                # Project updates (if assigned)
                for project in created_projects:
                    if user in project.assignees:
                        update = ProjectUpdate(
                            report_id=report.id,
                            project_id=project.id,
                            progress=f"Week {week_offset}: 진행 중입니다.",
                            issue=f"Week {week_offset}: 이슈 없음",
                            sales_support=f"Week {week_offset}: 기술 검토 중",
                            other_note="특이사항 없음"
                        )
                        db.session.add(update)

                # Sales Support
                sale = SalesSupport(
                    report_id=report.id,
                    project_id=random.choice(created_projects).id,
                    system="DCS",
                    company="ABC Corp",
                    schedule=str(week_start + timedelta(days=random.randint(0, 6))),
                    content="장비 제안 및 미팅",
                    companion="김정년"
                )
                db.session.add(sale)

                # Personal Schedule
                sched = PersonalSchedule(
                    report_id=report.id,
                    category=random.choice(['출장', '외근', '휴가', '휴일근무']),
                    person=user.name,
                    location="현장",
                    start_date=week_start,
                    end_date=week_start + timedelta(days=1),
                    start_time=datetime.strptime("09:00", "%H:%M").time(),
                    end_time=datetime.strptime("18:00", "%H:%M").time(),
                    description="현장 지원"
                )
                db.session.add(sched)

    db.session.commit()
    print("✅ Generated reports and projects for 4 weeks.")
