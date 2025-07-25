document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('solution-container');
    const addButton = document.getElementById('add-solution-btn');
    const solutionTemplate = document.getElementById('solution-template');
    const projectTemplate = document.getElementById('project-template');

    addButton.addEventListener('click', () => {
      const solutionClone = solutionTemplate.content.cloneNode(true);
      const solutionSelect = solutionClone.querySelector('.solution-select');

      solutionItems.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id;
        option.text = item.name;
        solutionSelect.appendChild(option);
      });

      container.appendChild(solutionClone);
    });

    // Event delegation for dynamic elements
    container.addEventListener('click', (e) => {
      if (e.target.classList.contains('remove-solution')) {
        e.target.closest('.solution-wrapper').remove();
      }

      if (e.target.classList.contains('add-project')) {
        const wrapper = e.target.closest('.solution-wrapper');
        const selectedSolutionId = wrapper.querySelector('.solution-select').value;

        if (!selectedSolutionId) {
          alert("Please select a solution first.");
          return;
        }

        const projects = projectsBySolution[selectedSolutionId] || [];
        if (projects.length === 0) {
          alert("No projects available for this solution.");
          return;
        }

        const projectClone = projectTemplate.content.cloneNode(true);
        const projectSelect = projectClone.querySelector('.project-select');
        const detailSection = projectClone.querySelector('.project-details');

        projects.forEach(project => {
          const option = document.createElement('option');
          option.value = project.id;
          option.text = project.project_name;
          projectSelect.appendChild(option);
        });

        projectSelect.addEventListener('change', () => {
          if (projectSelect.value) {
            detailSection.style.display = 'block';
          } else {
            detailSection.style.display = 'none';
          }
        });

        wrapper.appendChild(projectClone);
      }

      if (e.target.classList.contains('remove-project')) {
        e.target.closest('.project-wrapper').remove();
      }
    });
  });