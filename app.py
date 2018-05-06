from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from flask_sslify import SSLify
import os

# main
app = Flask(__name__)
app.config['SECRET_KEY'] = 'z0hnjGHAPfNXegURQXKwl8GASKmsyMVzVCUACXtFd6r2y3vDw0'
socketio = SocketIO(app)

# users
users = 0
db = {}

if 'DYNO' in os.environ: 
    # only trigger SSLify if the app is running on Heroku
    sslify = SSLify(app, permanent=True)

@app.route("/")
def hello():
    return render_template("index.html")

@socketio.on('message', namespace='/v1')
def handle_message(message):
    emit("new message", message, broadcast=True)

@socketio.on('new user', namespace='/v1')
def new_user_event(user):
    db[request.sid] = user
    print(f"{user} joined the room")
    emit('user joined', user, broadcast=True)

@socketio.on('typing', namespace='/v1')
def typing(data):
    emit('typing', data, json=True, broadcast=True)

@socketio.on('stop typing', namespace='/v1')
def stop_typing(data):
    emit('stop typing', data, json=True, broadcast=True)

@socketio.on('connect', namespace='/v1')
def new_connection():
    global users

    users += 1
    print(f"{users} users connected. 1 user joined")
    emit('status', users, broadcast=True)

@socketio.on('disconnect', namespace='/v1')
def dropped_connection():
    global users

    users -= 1
    try:
        print(f"{users} users connected. {db[request.sid]} left")
        emit('user left', db.pop(request.sid), broadcast=True)
        emit('status', users, broadcast=True)
    except KeyError:
        pass

if __name__ == '__main__':
    socketio.run(app)
