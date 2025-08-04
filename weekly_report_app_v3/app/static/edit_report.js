document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('solution-container');
  const addButton = document.getElementById('add-solution-btn');
  const solutionModal = document.getElementById('solution-modal');
  const cancelSolutionBtn = document.getElementById('cancel-add-solution');
  const solutionTable = document.getElementById('solution-table');
  const projectModal = document.getElementById('project-modal');
  const projectTableBody = document.querySelector('#project-table tbody');
  const cancelProjectBtn = document.getElementById('cancel-project-selection');

  const solutionTemplate = document.getElementById('solution-template');
  const projectTemplate = document.getElementById('project-template');

  let activeProjectWrapper = null;
  let activeSolutionId = null;

  addButton.addEventListener('click', () => {
    solutionModal.style.display = 'block';
  });

  cancelSolutionBtn.addEventListener('click', () => {
    solutionModal.style.display = 'none';
  });

  solutionTable.addEventListener('click', (e) => {
    const row = e.target.closest('.solution-row');
    if (!row) return;

    const id = row.dataset.id;
    const name = row.dataset.name;

    const wrapper = solutionTemplate.content.cloneNode(true);
    wrapper.querySelector('.solution-id').value = id;
    wrapper.querySelector('.selected-solution-name').textContent = name;

    container.appendChild(wrapper);
    solutionModal.style.display = 'none';
  });

  container.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-solution')) {
      e.target.closest('.solution-wrapper').remove();
    }

    if (e.target.classList.contains('add-project')) {
      const solutionWrapper = e.target.closest('.solution-wrapper');
      const solutionId = solutionWrapper.querySelector('input.solution-id').value;
      if (!solutionId) return alert("Please select a solution first.");

      const projects = projectsBySolution[solutionId] || [];
      if (!projects.length) return alert("No projects available for this solution.");

      activeProjectWrapper = solutionWrapper;
      activeSolutionId = solutionId;

      projectTableBody.innerHTML = '';
      projects.forEach(project => {
        const row = document.createElement('tr');
        row.className = 'project-row';
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
    if (!row) return;

    const project = JSON.parse(row.dataset.project);
    const projectBlock = projectTemplate.content.cloneNode(true);

    projectBlock.querySelector('.project-id').value = project.id;
    projectBlock.querySelector('.project-details').style.display = 'block';
    projectBlock.querySelector('.project-solution-name').textContent = solutionItems.find(s => s.id == activeSolutionId)?.name || '';
    projectBlock.querySelector('.project-location').textContent = project.location || '-';
    projectBlock.querySelector('.project-company').textContent = project.company || '-';
    projectBlock.querySelector('.project-name').textContent = project.project_name || '-';
    projectBlock.querySelector('.project-code').textContent = project.code || '-';
    projectBlock.querySelector('.project-assignees').textContent = (project.assignees || []).map(a => typeof a === 'object' ? a.name : a).join(', ') || '-';

    activeProjectWrapper.appendChild(projectBlock);
    projectModal.style.display = 'none';
    activeProjectWrapper = null;
    activeSolutionId = null;
  });
});
