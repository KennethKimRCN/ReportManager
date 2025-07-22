from app import db
from app.models import SolutionItem, Project
from datetime import datetime

# Sample parsed data from your list
raw_projects = [
    #Solution Item / Location / Company / Project Name / Project Code
    ("OTS", "여수", "금호미쓰이화학", "CA/FOX OTS", "E388672J00"),
    ("OTS", "말레이시아", "OCI TerraSus(구 OCIM)", "OCI Polysilicon OTS Project", "E385102J00"),
    ("APC", "광양", "POSCO", "광양포스코 #15산소공장 APC PJT", "E385932J00"),
    ("APC", "여수", "한화솔루션", "한화솔루션 COSMOS SOP & APC PJT", "E375592J00"),
    ("APC", "여수", "한화솔루션", "한화솔루션 여수공장&VCM2, TDI#3 APC 확대 구축PJT", "E351162J00"),
    ("APC", "울산", "KEP", "KEP APC PJT", "NA"),
    ("KBC(Petro-SIM)", "대전", "SK이노베이션", "SK이노베이션 Petro-SIM 5 years lease PJT", "NA"),
    ("PIMS", "몽골", "TPP4", "PIMS upgrade", "E390332J00"),
    ("PIMS", "여수", "H&G chemical", "RTDB 도입", "E390332J00"),
    ("PIMS", "서산", "현대오일뱅크", "Trend Server", "POC"),
    ("AMS", "당진", "한국가스공사", "AMS 신규 도입", "E333032J00"),
    ("AMS", "울산", "SK Energy", "AMS Maintenance", "NA"),
    ("ADMS", "울산", "S-OIL", "ADMS신규도입", "E390332J00"),
    ("MPA", "광양", "POSCO, RISK", "[RIST]산소공장 15,16 Plant SOP Sequence Program(Exapilot)", "E380882J00"),
    ("MPA", "광양", "POSCO, RISK", "RIST/POSCO/12&16 Plant SOP", "E394322J00"),
    ("MPA", "안산", "강남화성", "[KNC]Urethan1(PU21 Plant)_DCS Revamping PJT", "E394462J00"),
    ("MPA", "울산", "SK에너지", "SK에너지 MPA AMC", "E394322J00"),
    ("MPA", "여수", "한화솔루션", "[한화솔루션] CA6 APC & MPA COSMOS PJT", "E375592J00"),
    ("NCK", "평택", "NCK", "B1, B2 로직 개선 PJT", "_____2J00"),  # 수주 전
    ("AHI", "사내", "YKO 사내 프로젝트", "BEMS & 공조기 자율운전 구축", "-"),
    ("LIMS", "여수", "롯데GS화학", "분석정보시스템(LIMS) 구축", "E383302J00"),
    ("LIMS", "평택", "레조낙 코리아", "분석정보시스템(LIMS) 구축", "E360022J00"),
    ("OM", "울산", "S-OIL", "IO_TEM", "E373512J00"),
]

def import_projects(data):
    for solution_name, location, company, project_name, code in data:
        # Find or create the solution item
        solution_item = SolutionItem.query.filter_by(name=solution_name).first()
        if not solution_item:
            solution_item = SolutionItem(name=solution_name)
            db.session.add(solution_item)
            db.session.flush()  # Assigns an ID before creating related project

        # Avoid duplicates by checking if project code exists (if provided)
        if code and Project.query.filter_by(code=code).first():
            print(f"Project with code {code} already exists. Skipping.")
            continue

        # Create project
        project = Project(
            solution_item=solution_item,
            solution_name=solution_name,
            company=company if company else "N/A",
            location=location,
            project_name=project_name,
            code=code if code else f"UNDEFINED-{solution_name[:3]}-{location[:2]}-{datetime.utcnow().timestamp()}"
        )

        db.session.add(project)
    
    db.session.commit()
    print("Import completed.")

# Run import
import_projects(raw_projects)
