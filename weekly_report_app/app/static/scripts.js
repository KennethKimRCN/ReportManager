function toggleSection(id) {
    const el = document.getElementById(id);
    el.classList.toggle('open');
  }
  
  // --- Add Schedule ---
  function addSchedule() {
    const container = document.getElementById('scheduleContainer');
    const div = document.createElement('div');
    div.innerHTML = `
      <select name="schedule_category[]">
        <option>출장</option><option>외근</option><option>휴가</option><option>휴일근무</option>
      </select>
      <input name="schedule_title[]" placeholder="Title" required>
      <input name="schedule_location[]" placeholder="Location" required>
      <input type="date" name="schedule_start[]" required>
      <input type="date" name="schedule_end[]" required>
      <textarea name="schedule_description[]" placeholder="Details..."></textarea>
      <input type="text" name="companions[]" placeholder="Companions (comma-separated)">
      <hr>
    `;
    container.appendChild(div);
  }
  
  // --- Add Solution Item ---
  function addSolution() {
    const container = document.getElementById('solutionContainer');
    const div = document.createElement('div');
    const index = container.children.length;
  
    div.id = `solution-${index}`;
    div.innerHTML = `
      <input name="solution_name[]" placeholder="Solution Name" required>
      <div class="projects"></div>
      <button type="button" onclick="addProject(this)">+ Add Project</button>
      <hr>
    `;
    container.appendChild(div);
  }
  
  // --- Add Project Under Solution ---
  function addProject(button) {
    const container = button.previousElementSibling;
    const div = document.createElement('div');
    div.innerHTML = `
      <input name="project_name[]" placeholder="Project Name" required>
      <textarea name="project_progress[]" placeholder="Progress..." required></textarea>
      <input type="text" name="project_assignees[]" placeholder="Assignee IDs (comma-separated)">
      <hr>
    `;
    container.appendChild(div);
  }
  
  // --- Popup Project Selector ---
  function openProjectPopup() {
    document.getElementById('projectPopup').style.display = 'block';
  }
  
  function applyProjects() {
    const checkboxes = document.querySelectorAll('#projectList input[type="checkbox"]:checked');
    checkboxes.forEach(checkbox => {
      const project = JSON.parse(checkbox.dataset.project);
      insertProjectFromPopup(project);
    });
    document.getElementById('projectPopup').style.display = 'none';
  }
  
  function insertProjectFromPopup(project) {
    const solutionContainer = document.getElementById('solutionContainer');
  
    let solutionDiv = Array.from(solutionContainer.children).find(div =>
      div.querySelector('input[name="solution_name[]"]')?.value === project.solution_name
    );
  
    if (!solutionDiv) {
      addSolution();
      solutionDiv = solutionContainer.lastElementChild;
      solutionDiv.querySelector('input[name="solution_name[]"]').value = project.solution_name;
    }
  
    const projectArea = solutionDiv.querySelector('.projects');
    const projectDiv = document.createElement('div');
    projectDiv.innerHTML = `
      <input type="hidden" name="project_id[]" value="${project.id}">
      <input readonly value="${project.project_name}">
      <textarea name="project_progress[]" placeholder="Progress..." required></textarea>
      <input type="text" name="project_assignees[]" placeholder="Assignee IDs (comma-separated)">
      <hr>
    `;
    projectArea.appendChild(projectDiv);
  }
  