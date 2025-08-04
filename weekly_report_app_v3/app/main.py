from flask import render_template, jsonify, redirect, request, url_for, flash
from app import create_app
from app.models import *
import requests
import json

app = create_app()

@app.route('/')
def index():
    return redirect('/users')

@app.route('/users')
def show_users():
    users = User.query.all()
    return render_template('users.html', users=users)


############ Reports ############
@app.route('/reports')
def show_reports():
    reports = Report.query.all()

    # Create a list of tuples (report, formatted_year_week)
    reports_with_yrwk = []
    for report in reports:
        # Format year and week as "Y25 W30"
        year_short = f"Y{report.year % 100:02d}"
        week_str = f"W{report.week}"
        formatted_yrwk = f"{year_short} {week_str}"
        reports_with_yrwk.append((report, formatted_yrwk))

    return render_template('reports.html', reports_with_yrwk=reports_with_yrwk)

@app.route('/reports/<int:report_id>/edit', methods=['GET'])
def edit_report(report_id):
    report = Report.query.get_or_404(report_id)

    solution_items = [{"id": s.id, "name": s.name} for s in SolutionItem.query.order_by(SolutionItem.name).all()]

    projects_by_solution = {}
    for project in Project.query.order_by(Project.project_name).all():
        entry = {
            "id": project.id,
            "project_name": project.project_name,
            "location": project.location,
            "company": project.company,
            "code": project.code or "-",
            "assignees": [a.name for a in project.assignees] if hasattr(project, "assignees") else []
        }
        projects_by_solution.setdefault(project.solution_item_id, []).append(entry)

    existing_updates = []
    for update in report.project_updates:
        p = update.project
        s = p.solution_item
        existing_updates.append({
            "solution_id": s.id,
            "solution_name": s.name,
            "project_id": p.id,
            "project_name": p.project_name,
            "location": p.location,
            "company": p.company,
            "code": p.code or "-",
            "assignees": [{"name": a.name} for a in update.assignees],
            "schedule": update.schedule or "",
            "progress": update.progress or "",
            "issue": update.issue or ""
        })

    return render_template(
        'edit_report.html',
        report=report,
        solution_items=solution_items,
        projects_by_solution=projects_by_solution,
        existing_updates=existing_updates
    )

@app.route('/reports/<int:report_id>/edit', methods=['POST'])
def update_report(report_id):
    report = Report.query.get_or_404(report_id)

    report.solution_items.clear()
    selected_ids = request.form.getlist('solution_item_ids[]')
    if selected_ids:
        solutions = SolutionItem.query.filter(SolutionItem.id.in_(selected_ids)).all()
        report.solution_items.extend(solutions)

    ProjectUpdate.query.filter_by(report_id=report.id).delete()

    project_ids = request.form.getlist('project_ids[]')
    schedules = request.form.getlist('schedules[]')
    progresses = request.form.getlist('progresses[]')
    issues = request.form.getlist('issues[]')

    for i in range(len(project_ids)):
        if not project_ids[i] or not progresses[i].strip():
            continue
        update = ProjectUpdate(
            report_id=report.id,
            project_id=int(project_ids[i]),
            schedule=schedules[i],
            progress=progresses[i],
            issue=issues[i]
        )
        db.session.add(update)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return redirect(url_for('edit_report', report_id=report.id))


############ Solution Items ############
@app.route('/solution-items')
def show_solution_items():
    solution_items = SolutionItem.query.all()
    return render_template('solution_items.html', solution_items=solution_items)

@app.route('/solutions/<int:solution_id>/edit', methods=['GET'])
def edit_solution(solution_id):
    solution_item = SolutionItem.query.get_or_404(solution_id)
    return render_template('edit_solutions.html', solution_item=solution_item)

@app.route('/solutions/<int:solution_id>/edit', methods=['POST'])
def update_solution(solution_id):
    solution_item = SolutionItem.query.get_or_404(solution_id)

    # Update fields from form
    solution_item.name = request.form['name']
    solution_item.issue = request.form['issue']

    # Commit changes
    try:
        db.session.commit()
        #flash('Solution Item updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        #flash(f'Error updating Solution Item: {e}', 'danger')

    return redirect(url_for('edit_solution', solution_id=solution_item.id))


############ Projects ############
@app.route('/projects')
def show_projects():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@app.route('/projects/<int:project_id>/edit', methods=['GET'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('edit_project.html', project=project)

@app.route('/projects/<int:project_id>/edit', methods=['POST'])
def update_project(project_id):
    project = Project.query.get_or_404(project_id)

    project.location = request.form['location']
    project.company = request.form['company']
    project.project_name = request.form['project_name']
    project.code = request.form['code']

    code_val = request.form['code'].strip()
    project.code = code_val if code_val else None  # Set None if empty string

    db.session.commit()
    #flash('Project updated successfully!', 'success')
    return redirect(url_for('show_projects'))  # Redirect back to projects list page


############ Project Updates ############
@app.route('/project-updates')
def show_project_updates():
    project_updates = ProjectUpdate.query.all()
    return render_template('project_updates.html', project_updates=project_updates)

############ LLM ############ WORK IN PROGRESS
# Map model names to SQLAlchemy ORM classes
MODEL_MAP = {
    "User": User,
    "Project": Project,
    "Report": Report,
}

# Helper: serialize SQLAlchemy model instance to dict
def model_to_dict(obj):
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def call_llm(prompt, max_tokens=200, temperature=0):
    """
    Calls LM Studio's LLM API with the given prompt.
    """
    url = 'http://127.0.0.1:1234/v1/completions'  # adjust if needed
    payload = {
        "model": "llama-3.2-1b-instruct",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data.get('choices', [{}])[0].get('text', '')


@app.route('/ask-llm', methods=['POST'])
def query():
    """
    Main route: accept natural language query, convert it via LLM to JSON query,
    build SQLAlchemy query safely, and return results.
    """
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    # Step 1: Build prompt for LLM to convert NL query into JSON ORM query
    llm_prompt = (
        "You are an assistant that converts natural language queries about weekly reports "
        "into JSON objects describing ORM queries. The JSON format is:\n"
        "{\n"
        '  "model": "<ModelName>",\n'
        '  "filters": {\n'
        '    "field1": "value1",\n'
        '    "field2": "value2",\n'
        '    ...\n'
        '  }\n'
        "}\n"
        "Only output valid JSON, no explanations.\n"
        f"Natural language query: \"{user_query}\""
    )

    try:
        json_text = call_llm(llm_prompt)
        # Try to parse JSON safely
        query_json = json.loads(json_text)
    except Exception as e:
        return jsonify({'error': 'Failed to parse LLM response as JSON', 'details': str(e), 'llm_output': json_text}), 400

    model_name = query_json.get("model")
    filters = query_json.get("filters", {})

    if model_name not in MODEL_MAP:
        return jsonify({'error': f'Unknown model requested: {model_name}'}), 400

    model = MODEL_MAP[model_name]

    # Build filter conditions safely, whitelist only model columns
    valid_columns = {c.name for c in model.__table__.columns}
    filter_conditions = []
    for field, value in filters.items():
        if field not in valid_columns:
            return jsonify({'error': f'Invalid filter field: {field}'}), 400
        filter_conditions.append(getattr(model, field) == value)

    # Query DB
    results = db.session.query(model).filter(*filter_conditions).all()
    results_json = [model_to_dict(r) for r in results]

    return jsonify(results_json)



@app.route('/ask')
def ask_page():
    return render_template('llm_query.html')


if __name__ == '__main__':
    app.run(debug=True)
