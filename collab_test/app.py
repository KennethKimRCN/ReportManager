import eventlet
from flask import Flask, render_template, request, redirect, session, url_for
from flask_socketio import SocketIO, emit, join_room

eventlet.monkey_patch()

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

users = {}       # user_id -> {'name': ..., 'sid': ..., 'cursor': ...}
document = {
    "schedule": "",
    "progress": "",
    "notes": ""
}

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        user_id = request.form['user_id']
        session['name'] = name
        session['user_id'] = user_id
        return redirect('/editor')
    return render_template('login.html')

@app.route('/editor')
def editor():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('editor.html', name=session['name'], user_id=session['user_id'])

@socketio.on('connect')
def handle_connect():
    pass

@socketio.on('join')
def handle_join(data):
    user_id = data['user_id']
    name = data['name']
    users[user_id] = {'name': name, 'sid': request.sid, 'cursor': None}
    emit('user_list', users, broadcast=True)
    emit('load_document', document, room=request.sid)

@socketio.on('update_field')
def handle_update(data):
    field = data['field']
    value = data['value']
    document[field] = value
    emit('update_field', data, broadcast=True, include_self=False)

@socketio.on('cursor_move')
def handle_cursor(data):
    user_id = data['user_id']
    users[user_id]['cursor'] = data['cursor']
    emit('update_cursor', {'user_id': user_id, 'cursor': data['cursor']}, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    to_remove = None
    for uid, u in users.items():
        if u['sid'] == request.sid:
            to_remove = uid
            break
    if to_remove:
        del users[to_remove]
        emit('user_list', users, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
