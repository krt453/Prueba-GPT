from flask import Flask, request, jsonify, session
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.games = {}
app.next_id = 1


def login_required(fn):
    """Simple decorator to require authentication."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            return jsonify({'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)

    return wrapper


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if data.get('username') == 'admin' and data.get('password') == 'secret':
        session['user'] = data['username']
        return jsonify({'message': 'logged in'})
    return jsonify({'error': 'Unauthorized'}), 401


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user', None)
    return jsonify({'message': 'logged out'})


@app.route('/games', methods=['GET'])
def list_games():
    return jsonify(list(app.games.values()))


@app.route('/games', methods=['POST'])
@login_required
def create_game():
    data = request.get_json() or {}
    game = {
        'id': app.next_id,
        'name': data.get('name'),
        'genre': data.get('genre'),
    }
    app.games[app.next_id] = game
    app.next_id += 1
    return jsonify(game), 201


@app.route('/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = app.games.get(game_id)
    if not game:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(game)


@app.route('/games/<int:game_id>', methods=['PUT'])
@login_required
def update_game(game_id):
    game = app.games.get(game_id)
    if not game:
        return jsonify({'error': 'Not found'}), 404
    data = request.get_json() or {}
    if 'name' in data:
        game['name'] = data['name']
    if 'genre' in data:
        game['genre'] = data['genre']
    return jsonify(game)


@app.route('/games/<int:game_id>', methods=['DELETE'])
@login_required
def delete_game(game_id):
    if game_id in app.games:
        del app.games[game_id]
        return '', 204
    return jsonify({'error': 'Not found'}), 404

@app.route('/')
def home():
    return '¡Bienvenido a Game Hub!'

if __name__ == '__main__':
    app.run()
