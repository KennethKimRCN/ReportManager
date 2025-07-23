from app import db
from app.models import SolutionItem, Project, User
from datetime import datetime
import re

# 🔽 Paste your full raw project list here
raw_data = """
OTS / 여수 / 금호미쓰이화학 / CA/FOX OTS / E388672J00 / 양우성 차장, 김민욱 차장, 김정은 대리
OTS / 말레이시아 / OCI TerraSus(구 OCIM) / OCI Polysilicon OTS Project / E385102J00 / 양우성 차장, 김민욱 차장, 김정은 대리
APC / 광양 / POSCO / 광양포스코 #15산소공장 APC PJT / E385932J00 / 양우성 차장, 유세훈 과장, 오윤석 대리, 유혜빈 사원 
APC / 여수 / 한화솔루션 / 한화솔루션 COSMOS SOP & APC PJT / E375592J00 / 유세훈 과장, 오윤석 대리
APC / 여수 / 한화솔루션 / 한화솔루션 여수공장&VCM2, TDI#3 APC 확대 구축PJT / E351162J00 / 유세훈 과장, 유혜빈 사원
APC / 울산 / KEP / KEP APC PJT / 미정 / 유세훈 과장, 오윤석 대리
KBC(Petro-SIM) / 대전 / SK이노베이션 / SK이노베이션 Petro-SIM 5 years lease PJT / NA / 유세훈 과장
PIMS / 몽골 / TPP4 / PIMS upgrade / E390332J00 / 노덕기 차장
PIMS / 여수 / H&G chemical / RTDB 도입 / E390332J00 / 노덕기 차장, 민준홍 차장
PIMS / 서산 / 현대오일뱅크 / Trend Server / POC / 노덕기 차장
AMS / 당진 / 한국가스공사 / AMS 신규 도입 / E333032J00 / 노덕기 차장
AMS / SK Energy / AMS Maintenance / NA / 김강년 대리
ADMS / 울산 / S-OIL / ADMS신규도입 / E390332J00 / 노덕기 차장
MPA / 광양 / POSCO, RISK / [RIST]산소공장 15,16 Plant SOP Sequence Program(Exapilot) / E380882J00 / 양우성 차장, 김정년 대리, 황태경 대리
MPA / 광양 / POSCO, RISK / RIST/POSCO/12&16 Plant SOP / E394322J00 / 양우성 차장, 황태경 대리, 김정년 대리
MPA / 안산 / 강남화성 / [KNC]Urethan1(PU21 Plant)_DCS Revamping PJT / E394462J00 / 김정년 대리 (PM 손재락 부장)
MPA / 울산 / SK에너지 / SK에너지 MPA AMC / E394322J00 / 김정년 대리, 황태경 대리
MPA / 여수 / 한화솔루션 / [한화솔루션] CA6 APC & MPA COSMOS PJT / E375592J00 / 양우성 차장, 김정년 대리
NCK / 평택 / NCK / B1, B2 로직 개선 PJT / _____2J00(수주 전) / 황태경 대리 (PM 임성진 부서장)
AHI / YKO 사내 프로젝트 / BEMS & 공조기 자율운전 구축 / - / 민준홍 차장
LIMS / 여수 / 롯데GS화학 / 분석정보시스템(LIMS) 구축 / E383302J00 / 양우성 차장, 황태경 대리 Closing and 잔업업무?
LIMS / 평택 / 레조낙 코리아 / 분석정보시스템(LIMS) 구축 / E360022J00 / 황태경 대리
OM / 울산 / S-OIL / IO_TEM / E373512J00 / 노덕기 차장, 김강년 대리, 박현민 대리
"""

def parse_project_line(line):
    try:
        solution, location, company, project_name, code, assignee_str = map(str.strip, line.split(' / ', 5))
    except ValueError:
        print(f"❌ Skipping malformed line: {line}")
        return None

    # Parse assignees: "홍길동 차장, 이영희 대리"
    assignees = []
    for entry in re.split(r',\s*', assignee_str):
        match = re.match(r'([\w가-힣]+)\s+([가-힣]+)', entry.strip())
        if match:
            name, position = match.groups()
            assignees.append((name, position))
        else:
            print(f"⚠️ Skipping malformed assignee: {entry.strip()}")

    return {
        "solution": solution,
        "location": location,
        "company": company,
        "project_name": project_name,
        "code": code,
        "assignees": assignees
    }

def import_projects(raw_data):
    lines = raw_data.strip().splitlines()
    for line in lines:
        data = parse_project_line(line)
        if not data:
            continue

        # Create or find SolutionItem
        solution_name = data['solution']
        solution = SolutionItem.query.filter_by(name=solution_name).first()
        if not solution:
            print(f"➕ Creating new SolutionItem: {solution_name}")
            solution = SolutionItem(name=solution_name)
            db.session.add(solution)
            db.session.flush()

        # Create or find Project
        project = Project.query.filter_by(code=data['code']).first()
        if not project:
            project = Project(
                solution_item=solution,
                location=data['location'],
                company=data['company'],
                project_name=data['project_name'],
                code=data['code'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(project)
            db.session.flush()

        # Add default assignees
        for name, position in data['assignees']:
            user = User.query.filter_by(name=name, position=position).first()
            if not user:
                user = User(
                    name=name,
                    position=position,
                    employee_id=f"TEMP-{name}",
                    email=f"{name}@example.com",
                    is_active=True
                )
                db.session.add(user)
                db.session.flush()

            if user not in project.default_assignees:
                project.default_assignees.append(user)

    db.session.commit()
    print("✅ Bulk project import complete.")

# Run with Flask app context
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        import_projects(raw_data)
