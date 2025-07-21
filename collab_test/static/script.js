function saveField(fieldId) {
    const value = document.getElementById(fieldId).value;
    fetch('/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `field=${fieldId}&value=${encodeURIComponent(value)}`
    });
}

function loadData() {
    fetch('/get_project')
        .then(response => response.json())
        .then(data => {
            ['schedule', 'progress', 'other_notes'].forEach(id => {
                const el = document.getElementById(id);
                if (el !== document.activeElement) {
                    el.value = data[id];
                }
            });
        });
}

['schedule', 'progress', 'other_notes'].forEach(id => {
    const el = document.getElementById(id);
    el.addEventListener('input', () => saveField(id));
});

setInterval(loadData, 2000);
