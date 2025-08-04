const socket = io();
socket.emit('join', { user_id: USER_ID, name: NAME });

const fields = ['schedule', 'progress', 'notes'];

fields.forEach(field => {
  const el = document.getElementById(field);
  el.addEventListener('input', () => {
    socket.emit('update_field', { field: field, value: el.value });
  });

  el.addEventListener('keyup', () => {
    const pos = el.selectionStart;
    socket.emit('cursor_move', { user_id: USER_ID, cursor: pos });
  });
});

socket.on('load_document', (data) => {
  fields.forEach(f => {
    document.getElementById(f).value = data[f];
  });
});

socket.on('update_field', (data) => {
  document.getElementById(data.field).value = data.value;
});

socket.on('user_list', (users) => {
  const div = document.getElementById('users');
  div.innerHTML = '<h4>Active Users</h4>';
  for (let id in users) {
    const u = users[id];
    div.innerHTML += `<p>${u.name} (ID: ${id})</p>`;
  }
});

socket.on('update_cursor', (data) => {
  console.log(`User ${data.user_id} moved cursor to ${data.cursor}`);
});
