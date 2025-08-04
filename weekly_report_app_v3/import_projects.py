from app import db, create_app
from app.models import SolutionItem, Project, User
from datetime import datetime, timezone
import random

app = create_app()

# Updated raw project data format: tuple with assignee names
# (solution, location, company, name, code, assignees_str)
raw_projects_with_assignees = [
    ("OTS", "울산", "S-OIL", "SHAHEEN PKG#1", "E351882J00", "김민욱, 김정은"),
    ("OTS", "말레이시아", "OCI TerraSus(구 OCIM)", "OCI Polysilicon OTS Project", "E385102J00", "양우성, 김민욱, 김정은"),
    ("APC", "광양", "POSCO", "광양포스코 #15산소공장 APC PJT", "E385932J00", "양우성, 유세훈, 오윤석, 유혜빈"),
    ("KBC(Petro-SIM)", "대전", "SK이노베이션", "SK이노베이션 Petro-SIM 5 years lease PJT", "NA", "유세훈"),
    ("PIMS", "몽골", "TPP4", "PIMS upgrade", "E390332J00", "노덕기"),
    ("PIMS", "여수", "H&G chemical", "RTDB 도입", "E390332J00", "노덕기, 민준홍"),
    ("PIMS", "서산", "현대오일뱅크", "Trend Server", "POC", "노덕기"),
    ("PIMS", "울산", "K&D에너젠", "BNF Hanprism", "E381362J00", "노덕기"),
    ("AMS", "당진", "한국가스공사", "AMS 신규 도입", "E333032J00", "노덕기"),
    ("AMS", "울산", "SK Energy", "AMS Maintenance", "Exxxxx?", "김강년"),
    ("ADMS", "울산", "S-OIL", "ADMS신규도입", "E390332J00", "노덕기"),
    ("MPA", "광양", "POSCO, RISK", "[RIST]산소공장 15,16 Plant SOP Sequence Program(Exapilot)", "E380882J00", "양우성, 김정년, 황태경"),
    ("MPA", "광양", "POSCO, RISK", "RIST/POSCO/12&16 Plant SOP", "E394322J00", "양우성, 황태경, 김정년"),
    ("MPA", "안산", "강남화성", "[KNC]Urethan1(PU21 Plant)_DCS Revamping PJT", "E394462J00", "김정년"),
    ("MPA", "울산", "SK에너지", "SK에너지 MPA AMC", "E394322J00", "김정년, 황태경"),
    ("MPA", "여수", "한화솔루션", "[한화솔루션] CA6 APC & MPA COSMOS PJT", "E375592J00", "양우성, 김정년"),
    ("NCK", "평택", "NCK", "B1, B2 로직 개선 PJT", "E405922J00", "황태경"),
    ("AHI", "사내", "YKO 사내 프로젝트", "BEMS & 공조기 자율운전 구축", "-", "민준홍"),
    ("OM", "울산", "S-OIL", "IO_TEM", "E373512J00", "노덕기, 김강년, 박현민"),
]



def generate_undefined_code(solution_name, location):
    timestamp = int(datetime.now(timezone.utc).timestamp())
    rand_suffix = random.randint(100, 999)
    return f"UNDEF-{solution_name[:3]}-{location[:2]}-{timestamp}{rand_suffix}"

def find_user_by_name(full_name_with_rank):
    """
    Example input: "김민욱 차장"
    Tries to find a user with a matching name
    """
    name = full_name_with_rank.strip().split()[0]  # extract name only
    return User.query.filter_by(name=name).first()

def import_projects(data):
    with app.app_context():
        seen_codes = set()
        for solution_name, location, company, project_name, code, assignees_str in data:
            # Step 1: Solution Item
            solution_item = SolutionItem.query.filter_by(name=solution_name).first()
            if not solution_item:
                solution_item = SolutionItem(name=solution_name)
                db.session.add(solution_item)
                db.session.flush()

            # Step 2: Project Code Handling
            project_code = code.strip() if code else None
            if not project_code or project_code in ("-", "NA", "POC"):
                project_code = generate_undefined_code(solution_name, location)

            if project_code in seen_codes or Project.query.filter_by(code=project_code).first():
                print(f"Project with code {project_code} already exists or duplicated. Skipping.")
                continue

            seen_codes.add(project_code)

            # Step 3: Create Project
            project = Project(
                solution_item=solution_item,
                location=location,
                company=company or "N/A",
                project_name=project_name,
                code=project_code
            )

            db.session.add(project)
            db.session.flush()

            # Step 4: Assign Users
            assignee_names = [a.strip() for a in assignees_str.split(",") if a.strip()]
            for full_name in assignee_names:
                user = find_user_by_name(full_name)
                if user:
                    project.default_assignees.append(user)
                else:
                    print(f"⚠️ Warning: User '{full_name}' not found. Skipping assignment.")

        # Step 5: Commit All
        try:
            db.session.commit()
            print("Import with assignees completed.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to commit: {e}")

if __name__ == "__main__":
    import_projects(raw_projects_with_assignees)
