

@app.route('/')
@cache.cached(timeout=60)
def home():
    """Página de inicio."""
    return render_template('index.html')


@app.route('/games')
def games_list():
    """Muestra un listado de juegos."""
    return render_template('games.html', games=games)


@app.route('/games/<int:game_id>')
def game_detail(game_id: int):
    """Muestra el detalle de un juego por identificador."""
    game = next((g for g in games if g["id"] == game_id), None)
    if game is None:
        abort(404)
    return render_template('game_detail.html', game=game)

@socketio.on('update_score')
def handle_update_score(data):
    """Broadcast the updated score to all connected clients."""
    emit('score_updated', data, broadcast=True)


@socketio.on('send_message')
def handle_send_message(data):
    """Broadcast a chat message to all connected clients."""
    emit('receive_message', data, broadcast=True)


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username == 'admin' and password == 'password':
        token = create_access_token(identity=username)
        return jsonify(access_token=token)
    return jsonify({'error': 'Bad credentials'}), 401

if __name__ == '__main__':
    socketio.run(app)
