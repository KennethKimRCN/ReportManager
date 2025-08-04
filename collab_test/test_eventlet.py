import eventlet
eventlet.monkey_patch()

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello"

if __name__ == '__main__':
    app.run()
