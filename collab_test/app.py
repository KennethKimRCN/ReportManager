from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from threading import Lock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Document state
box1 = {"text": ""}
box2 = {"text": ""}
user_count = 0
lock = Lock()

# Permissions
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
    socketio.emit('user_count', {'count': user_count})

@socketio.on('disconnect')
def handle_disconnect():
    global user_count
    with lock:
        user_count = max(0, user_count - 1)
    socketio.emit('user_count', {'count': user_count})

@socketio.on('request_initial_data')
def send_initial_data():
    emit('load_texts', {"box1": box1["text"], "box2": box2["text"]})

@socketio.on('text_update')
def handle_text_update(data):
    username = data['username']
    box_id = data['box']
    text = data['text']

    # Update correct box if user has permission
    if username in permissions[box_id]:
        if box_id == "box1":
            box1["text"] = text
        elif box_id == "box2":
            box2["text"] = text
        emit('broadcast_text', data, broadcast=True, include_self=False)


if __name__ == '__main__':
    socketio.run(app, debug=True)
