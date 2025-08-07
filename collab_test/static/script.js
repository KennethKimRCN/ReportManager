const socket = io();
const box1 = document.getElementById('box1');
const box2 = document.getElementById('box2');
const userCountDisplay = document.getElementById('user-count');

// Track local changes
let localUpdate = false;

socket.on('connect', () => {
    socket.emit('request_initial_data');
});

// Load initial texts
socket.on('load_texts', data => {
    box1.value = data.box1;
    box2.value = data.box2;
});

socket.on('user_count', data => {
    userCountDisplay.textContent = data.count;
});

// Listen for external updates
socket.on('broadcast_text', data => {
    if (!localUpdate) {
        if (data.box === "box1") box1.value = data.text;
        if (data.box === "box2") box2.value = data.text;
    }
    localUpdate = false;
});

// Emit input changes
[box1, box2].forEach(input => {
    input.addEventListener('input', () => {
        localUpdate = true;
        const boxId = input.id;
        socket.emit('text_update', {
            username: USERNAME,
            box: boxId,
            text: input.value
        });
    });
});
