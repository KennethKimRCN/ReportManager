// Keep track of added project IDs to prevent duplicates
const addedProjects = new Set();

// Triggered by popup window on selection
function addProjectFromPopup(id, name, code) {
  if (addedProjects.has(id)) {
    alert("이미 추가된 프로젝트입니다.");
    return;
  }

  const container = document.getElementById("selected-projects");

  const projectDiv = document.createElement("div");
  projectDiv.classList.add("project-box");
  projectDiv.setAttribute("data-id", id);

  projectDiv.innerHTML = `
    <input type="hidden" name="project_ids" value="${id}">
    <div class="project-header">
      <h3>${name} (${code})</h3>
      <button type="button" class="remove-btn" onclick="removeProject('${id}')">❌</button>
    </div>

    <label>진행상황</label>
    <textarea name="project_${id}_progress" rows="3" required></textarea>

    <label>특이사항</label>
    <textarea name="project_${id}_issues" rows="3"></textarea>

    <label>영업지원 사항</label>
    <textarea name="project_${id}_sales_support" rows="3"></textarea>

    <label>그 외 특이사항</label>
    <textarea name="project_${id}_other_notes" rows="3"></textarea>
  `;

  container.appendChild(projectDiv);
  addedProjects.add(id);
}

// Remove project block by ID
function removeProject(id) {
  const container = document.getElementById("selected-projects");
  const block = container.querySelector(`[data-id="${id}"]`);
  if (block) {
    block.remove();
    addedProjects.delete(id);
  }
}

// Open popup for project selection
function openProjectPopup() {
  window.open('/project-popup', '프로젝트 선택', 'width=900,height=700');
}
