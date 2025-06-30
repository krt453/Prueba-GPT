from functools import wraps
from flask import Flask, jsonify, request, session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

# In-memory store for created games
_games = []
_next_id = 1

def login_required(fn):
    """Simple decorator that requires the user to be logged in."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            # Unauthorized when the user is not authenticated
            return '', 401
        return fn(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if username == 'admin' and password == 'secret':
        session['logged_in'] = True
        return jsonify(message='logged in')
    return '', 401

@app.route('/games', methods=['POST'])
@login_required
def create_game():
    global _next_id
    data = request.get_json() or {}
    game = {'id': _next_id, 'name': data.get('name')}
    _games.append(game)
    _next_id += 1
    return jsonify(game), 201

@app.route('/games/<int:gid>', methods=['GET'])
@login_required
def get_game(gid):
    for game in _games:
        if game['id'] == gid:
            return jsonify(game)
    return '', 404

@app.route('/games/<int:gid>', methods=['PUT'])
@login_required
def update_game(gid):
    data = request.get_json() or {}
    for game in _games:
        if game['id'] == gid:
            game['name'] = data.get('name', game['name'])
            return jsonify(game)
    return '', 404

@app.route('/games/<int:gid>', methods=['DELETE'])
@login_required
def delete_game(gid):
    for game in _games:
        if game['id'] == gid:
            _games.remove(game)
            return '', 204
    return '', 404

if __name__ == '__main__':
    app.run(debug=True)
