from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def home():
    return '¡Bienvenido a Game Hub!'

@socketio.on('update_score')
def handle_update_score(data):
    """Broadcast the updated score to all connected clients."""
    emit('score_updated', data, broadcast=True)


@socketio.on('send_message')
def handle_send_message(data):
    """Broadcast a chat message to all connected clients."""
    emit('receive_message', data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app)
