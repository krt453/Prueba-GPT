from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token

from game_api import api_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'change-this-secret'

jwt = JWTManager(app)
app.register_blueprint(api_bp)

@app.route('/')
def home():
    return '¡Bienvenido a Game Hub!'

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username == 'admin' and password == 'password':
        token = create_access_token(identity=username)
        return jsonify(access_token=token)
    return jsonify({'error': 'Bad credentials'}), 401

if __name__ == '__main__':
    app.run()
