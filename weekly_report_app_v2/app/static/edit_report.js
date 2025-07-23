window.onload = function () {
    if (window.reportData.solutions.length === 0) {
        addSolutionBlock();
    } else {
        window.reportData.solutions.forEach(sol => {
            const solBlock = addSolutionBlock();
            const select = solBlock.querySelector('.solution-select');
            select.value = sol.id;
            loadProjects(select, sol.projects);
        });
    }
};

function addSolutionBlock() {
    const container = document.getElementById('solutionsContainer');
    const tmpl = document.getElementById('solutionTemplate').content.cloneNode(true);
    const section = tmpl.querySelector('.solution-section');
    container.appendChild(section);
    return section;
}

function addProjectToSolution(btn) {
    const solBlock = btn.closest('.solution-section');
    const projectsContainer = solBlock.querySelector('.projects-container');
    const tmpl = document.getElementById('projectTemplate').content.cloneNode(true);
    projectsContainer.appendChild(tmpl);
}

function removeElement(el) {
    el.remove();
}

function loadProjects(selectEl, prefilledProjects=[]) {
    const solId = selectEl.value;
    const container = selectEl.closest('.solution-section').querySelector('.projects-container');
    container.innerHTML = '';
    if (!solId) return;

    fetch(`/projects/by_solution/${solId}`)
        .then(res => res.json())
        .then(projects => {
            if (prefilledProjects.length > 0) {
                prefilledProjects.forEach(proj => {
                    const tmpl = document.getElementById('projectTemplate').content.cloneNode(true);
                    const wrapper = tmpl.querySelector('.project-section');

                    const select = wrapper.querySelector('.project-select');
                    projects.forEach(p => {
                        const opt = document.createElement('option');
                        opt.value = p.id;
                        opt.textContent = `${p.code} - ${p.project_name}`;
                        select.appendChild(opt);
                    });
                    select.value = proj.id;

                    wrapper.querySelector('.schedule-field').value = proj.schedule || '';
                    wrapper.querySelector('.progress-field').value = proj.progress || '';
                    wrapper.querySelector('.issue-field').value = proj.issue || '';

                    const assigneeDiv = wrapper.querySelector('.assignees-display');
                    if (proj.assignees && proj.assignees.length) {
                        assigneeDiv.innerHTML = '<strong>Assignees:</strong> ' + proj.assignees.map(a => a.name).join(', ');
                    }

                    container.appendChild(wrapper);
                });
            }
        });
}

document.getElementById('reportForm').addEventListener('submit', function (e) {
    const data = {
        status: document.getElementById('status') ? document.getElementById('status').value : null,
        solutions: []
    };
    document.querySelectorAll('.solution-section').forEach(solBlock => {
        const solId = solBlock.querySelector('.solution-select').value;
        const solution = { id: parseInt(solId), projects: [] };
        solBlock.querySelectorAll('.project-section').forEach(projBlock => {
            const project = {
                id: parseInt(projBlock.querySelector('.project-select').value),
                schedule: projBlock.querySelector('.schedule-field').value,
                progress: projBlock.querySelector('.progress-field').value,
                issue: projBlock.querySelector('.issue-field').value
            };
            solution.projects.push(project);
        });
        data.solutions.push(solution);
    });
    document.getElementById('data_json').value = JSON.stringify(data);
});
