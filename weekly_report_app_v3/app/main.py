from flask import render_template, redirect, request, url_for, flash
from app import create_app
from app.models import *

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

    # Solution items for dropdown
    solution_items = [
        {"id": item.id, "name": item.name}
        for item in SolutionItem.query.order_by(SolutionItem.name).all()
    ]

    # Projects grouped by solution
    projects = Project.query.order_by(Project.project_name).all()
    projects_by_solution = {}
    for project in projects:
        sid = project.solution_item_id
        if sid not in projects_by_solution:
            projects_by_solution[sid] = []
        projects_by_solution[sid].append({
            "id": project.id,
            "project_name": project.project_name
        })

    # Existing project updates (to pre-render)
    existing_updates = []
    for update in report.project_updates:
        project = update.project
        solution = project.solution_item
        existing_updates.append({
            "solution_id": solution.id,
            "solution_name": solution.name,
            "project_id": project.id,
            "project_name": project.project_name,
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

    # 1. Update report status
    #report.status = request.form['status']

    # 2. Update solution item associations
    report.solution_items.clear()
    selected_ids = request.form.getlist('solution_item_ids')
    if selected_ids:
        selected_solutions = SolutionItem.query.filter(SolutionItem.id.in_(selected_ids)).all()
        report.solution_items.extend(selected_solutions)

    # 3. Clear previous ProjectUpdate entries
    ProjectUpdate.query.filter_by(report_id=report.id).delete()

    # 4. Re-add project updates from form
    project_ids = request.form.getlist('project_ids[]')
    schedules = request.form.getlist('schedules[]')
    progresses = request.form.getlist('progresses[]')
    issues = request.form.getlist('issues[]')

    for i in range(len(project_ids)):
        project_id = project_ids[i]
        schedule = schedules[i]
        progress = progresses[i]
        issue = issues[i]

        if not project_id or not progress.strip():
            continue  # skip incomplete entries

        update = ProjectUpdate(
            report_id=report.id,
            project_id=int(project_id),
            schedule=schedule,
            progress=progress,
            issue=issue
        )
        db.session.add(update)

    try:
        db.session.commit()
        # flash('Report updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        # flash(f'Error updating report: {e}', 'danger')

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

if __name__ == '__main__':
    app.run(debug=True)
