import os

base_structure = {
    "team_report_app": {
        "templates": {
            "index.html": "",
            "submit.html": "",
            "report.html": ""
        },
        "static": {
            "style.css": ""
        },
        "reports": {},
        "app.py": "",
        "models.py": "",
        "export.py": "",
        "requirements.txt": ""
    }
}

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    create_structure(".", base_structure)
    print("✅ Project structure created in ./team_report_app/")
