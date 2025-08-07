from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

box1 = {"text": ""}
box2 = {"text": ""}
user_count = 0
connected_users = set()
lock = Lock()

permissions = {
    "box1": {"A", "B"},
    "box2": {"B", "C"}
}

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'], permissions=permissions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('home'))
    return render_template('login.html')

@socketio.on('connect')
def handle_connect():
    global user_count
    with lock:
        user_count += 1
        # Add username to connected users if available in session
        # Flask session not available directly here, so we'll rely on handshake query
        username = None
        if 'username' in session:
            username = session['username']

        # But session isn't directly accessible here, so instead we'll expect username from client on connect event.
        # We'll update this below.

    # We can't reliably get username here, so defer user adding to a separate event

@socketio.on('register_user')
def register_user(data):
    global user_count
    username = data.get('username')
    with lock:
        connected_users.add(username)
        user_count = len(connected_users)
    socketio.emit('user_info', {'count': user_count, 'users': list(connected_users)})

@socketio.on('disconnect')
def handle_disconnect():
    # We don't know which username disconnected here directly,
    # so we need to track that on client disconnect
    # One approach is to track client sid → username mapping
    # Let's implement that:

    sid = request.sid
    with lock:
        username = sid_username_map.pop(sid, None)
        if username and username in connected_users:
            connected_users.remove(username)
        user_count = len(connected_users)
    socketio.emit('user_info', {'count': user_count, 'users': list(connected_users)})

sid_username_map = {}

@socketio.on('connect')
def on_connect():
    sid = request.sid
    # Just register the sid with no username yet
    sid_username_map[sid] = None

@socketio.on('register_user')
def on_register_user(data):
    sid = request.sid
    username = data.get('username')
    with lock:
        sid_username_map[sid] = username
        connected_users.add(username)
    socketio.emit('user_info', {'count': len(connected_users), 'users': list(connected_users)})

# Update the rest as before...

@socketio.on('request_initial_data')
def send_initial_data():
    emit('load_texts', {"box1": box1["text"], "box2": box2["text"]})

@socketio.on('text_update')
def handle_text_update(data):
    username = data['username']
    box_id = data['box']
    text = data['text']

    if username in permissions[box_id]:
        if box_id == "box1":
            box1["text"] = text
        elif box_id == "box2":
            box2["text"] = text
        emit('broadcast_text', data, broadcast=True, include_self=False)

if __name__ == '__main__':
    socketio.run(app, debug=True)
