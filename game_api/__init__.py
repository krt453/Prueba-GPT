from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

api_bp = Blueprint('api', __name__, url_prefix='/api')

games = []

@api_bp.route('/games', methods=['GET'])
@jwt_required()
def list_games():
    return jsonify(games)

@api_bp.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    data = request.get_json() or {}
    game = {'id': len(games) + 1, 'name': data.get('name')}
    games.append(game)
    return jsonify(game), 201

@api_bp.route('/games/<int:game_id>', methods=['PUT'])
@jwt_required()
def update_game(game_id):
    data = request.get_json() or {}
    for game in games:
        if game['id'] == game_id:
            game['name'] = data.get('name', game['name'])
            return jsonify(game)
    return jsonify({'error': 'Game not found'}), 404

@api_bp.route('/games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    for game in games:
        if game['id'] == game_id:
            games.remove(game)
            return '', 204
    return jsonify({'error': 'Game not found'}), 404
