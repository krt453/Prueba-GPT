import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from gamehub.models import db, Game, User

api_bp = Blueprint('api', __name__, url_prefix='/api')


def is_admin():
    uid = get_jwt_identity()
    if uid is None:
        return False
    user = User.query.filter_by(username=uid).first()
    return user is not None and user.role == 'admin'


@api_bp.route('/games', methods=['GET'])
@jwt_required()
def list_games():
    """Return all games stored in the database."""
    games = Game.query.all()
    return jsonify([g.to_dict() for g in games])

@api_bp.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    """Create a game using posted JSON."""
    if not is_admin():
        return '', 403
    data = request.get_json() or {}
    rd = data.get('release_date')
    if rd:
        try:
            rd = datetime.date.fromisoformat(rd)
        except ValueError:
            return jsonify({'error': 'Invalid release_date'}), 400
    game = Game(
        name=data.get('name'),
        description=data.get('description'),
        genre=data.get('genre'),
        release_date=rd,
    )
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict()), 201

@api_bp.route('/games/<int:game_id>', methods=['PUT'])
@jwt_required()
def update_game(game_id):
    """Update an existing game."""
    data = request.get_json() or {}
    game = Game.query.get(game_id)
    if game:
        game.name = data.get('name', game.name)
        if 'description' in data:
            game.description = data['description']
        if 'genre' in data:
            game.genre = data['genre']
        if 'release_date' in data:
            rd = data['release_date']
            game.release_date = (
                datetime.date.fromisoformat(rd) if rd else None
            )
        db.session.commit()
        return jsonify(game.to_dict())
    return jsonify({'error': 'Game not found'}), 404

@api_bp.route('/games/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    """Remove a game."""
    if not is_admin():
        return '', 403
    game = Game.query.get(game_id)
    if game:
        db.session.delete(game)
        db.session.commit()
        return '', 204
    return jsonify({'error': 'Game not found'}), 404
