document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('solution-container');
  const addButton = document.getElementById('add-solution-btn');
  const solutionTemplate = document.getElementById('solution-template');
  const projectTemplate = document.getElementById('project-template');

  // --- Solution Modal Elements ---
  const solutionModal = document.getElementById('solution-modal');
  const cancelSolutionBtn = document.getElementById('cancel-add-solution');
  const solutionTable = document.getElementById('solution-table');

  // --- Project Modal Elements ---
  const projectModal = document.getElementById('project-modal');
  const projectTableBody = document.querySelector('#project-table tbody');
  const cancelProjectBtn = document.getElementById('cancel-project-selection');

  // --- State holders ---
  let activeProjectWrapper = null;
  let activeSolutionId = null;

  // === SOLUTION MODAL ===
  addButton.addEventListener('click', () => {
    solutionModal.style.display = 'block';
  });

  cancelSolutionBtn.addEventListener('click', () => {
    solutionModal.style.display = 'none';
  });

  solutionTable.addEventListener('click', (e) => {
    const row = e.target.closest('.solution-row');
    if (!row) return;

    const selectedSolutionId = row.dataset.id;
    const selectedSolutionName = row.dataset.name;

    // Build solution wrapper
    const solutionWrapper = document.createElement('div');
    solutionWrapper.className = 'solution-wrapper';
    solutionWrapper.style = "margin-bottom: 12px; border: 1px solid #ccc; padding: 10px;";

    solutionWrapper.innerHTML = `
      <div class="solution-row">
        <button type="button" class="remove-solution">X</button>
        <label class="solution-label">솔루션: ${selectedSolutionName}</label>
        <input type="hidden" name="solution_item_ids[]" value="${selectedSolutionId}">
        <button type="button" class="add-project">Add Project</button>
      </div>
    `;

    container.appendChild(solutionWrapper);
    solutionModal.style.display = 'none';
  });

  // === PROJECT MODAL ===
  container.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-solution')) {
      e.target.closest('.solution-wrapper').remove();
    }

    if (e.target.classList.contains('add-project')) {
      const wrapper = e.target.closest('.solution-wrapper');
      const selectedSolutionId = wrapper.querySelector('input[name="solution_item_ids[]"]').value;


      if (!selectedSolutionId) {
        alert("Please select a solution first.");
        return;
      }

      const projects = projectsBySolution[selectedSolutionId] || [];
      if (projects.length === 0) {
        alert("No projects available for this solution.");
        return;
      }

      // Save active state
      activeProjectWrapper = wrapper;
      activeSolutionId = selectedSolutionId;

      // Populate project modal table
      projectTableBody.innerHTML = '';
      projects.forEach(project => {
        const row = document.createElement('tr');
        row.classList.add('project-row');
        row.style.cursor = 'pointer';
        row.dataset.project = JSON.stringify(project);

        row.innerHTML = `
          <td>${project.id}</td>
          <td>${project.location || '-'}</td>
          <td>${project.company || '-'}</td>
          <td>${project.project_name}</td>
          <td>${project.code || '-'}</td>
        `;
        projectTableBody.appendChild(row);
      });

      projectModal.style.display = 'block';
    }

    if (e.target.classList.contains('remove-project')) {
      e.target.closest('.project-wrapper').remove();
    }
  });

  cancelProjectBtn.addEventListener('click', () => {
    projectModal.style.display = 'none';
    activeProjectWrapper = null;
    activeSolutionId = null;
  });

  projectTableBody.addEventListener('click', (e) => {
    const row = e.target.closest('.project-row');
    if (!row || !activeProjectWrapper || !activeSolutionId) return;
  
    const project = JSON.parse(row.dataset.project);
  
    const projectClone = projectTemplate.content.cloneNode(true);
    
    projectClone.querySelector('.project-id').value = project.id;
    projectClone.querySelector('.project-details').style.display = 'block';
  
    projectClone.querySelector('.project-solution-name').textContent = solutionItems.find(s => s.id == activeSolutionId)?.name || '';
    projectClone.querySelector('.project-location').textContent = project.location || '-';
    projectClone.querySelector('.project-company').textContent = project.company || '-';
    projectClone.querySelector('.project-name').textContent = project.project_name || '-';
    projectClone.querySelector('.project-code').textContent = project.code || '-';
  
    // Assuming project.assignees is an array of names or user objects
    const assignees = project.assignees?.map(a => a.name || a).join(', ') || '-';
    projectClone.querySelector('.project-assignees').textContent = assignees;
  
    activeProjectWrapper.appendChild(projectClone);
  
    // Reset
    projectModal.style.display = 'none';
    activeProjectWrapper = null;
    activeSolutionId = null;
  });
});
