import os
import datetime
from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    abort,
    redirect,
    url_for,
)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from werkzeug.security import generate_password_hash, check_password_hash
from gamehub.models import db, Game, User
from gamehub.forms import GameForm
from game_api import api_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret')

jwt = JWTManager(app)


def current_user():
    """Return the authenticated user or None."""
    uname = get_jwt_identity()
    if uname is not None:
        return User.query.filter_by(username=uname).first()
    return None


def admin_required():
    user = current_user()
    if not user or user.role != "admin":
        return False
    return True

# Database configuration. Use environment variables defined in docker-compose
# and fall back to an in-memory SQLite database when they are missing (e.g. in
# tests).
mysql_host = os.getenv('MYSQL_HOST')
mysql_user = os.getenv('MYSQL_USER')
mysql_password = os.getenv('MYSQL_PASSWORD')
mysql_db = os.getenv('MYSQL_DATABASE')

if mysql_host and mysql_user and mysql_password and mysql_db:
    uri = f'mysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}'
else:
    uri = 'sqlite:///:memory:'

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    # Ensure an admin user exists for initial logins
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("secret"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()

app.register_blueprint(api_bp)


@app.route('/')
def home():
    """Simple greeting for the root path."""
    return '¡Bienvenido a Game Hub!'


@app.route('/games', methods=['GET'])
@jwt_required()
def games_list():
    """Render an HTML page with all games."""
    games = Game.query.all()
    return render_template('games.html', games=games, is_admin=admin_required())


@app.route('/register', methods=['POST'])
def register():
    """Create a new user account."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'user')
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User exists'}), 400
    user = User(
        username=username,
        password=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@app.route('/login', methods=['POST'])
def login():
    """Return a JWT if the credentials are valid."""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password or ""):
        token = create_access_token(identity=user.username)
        return jsonify(access_token=token, role=user.role)
    return '', 401

@app.route('/games', methods=['POST'])
@jwt_required()
def create_game():
    if not admin_required():
        return '', 403
    data = request.get_json() or {}
    release_date = data.get('release_date')
    if release_date:
        try:
            release_date = datetime.date.fromisoformat(release_date)
        except ValueError:
            return jsonify({'error': 'Invalid release_date'}), 400
    game = Game(
        name=data.get('name'),
        description=data.get('description'),
        genre=data.get('genre'),
        release_date=release_date,
    )
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict()), 201

@app.route('/games/<int:gid>', methods=['GET'])
@jwt_required()
def get_game(gid):
    game = db.session.get(Game, gid)
    if game:
        return jsonify(game.to_dict())
    return '', 404


@app.route('/games/view/<int:gid>', methods=['GET'])
@jwt_required()
def game_detail_page(gid):
    """Render details of a game using a template."""
    game = db.session.get(Game, gid) or abort(404)
    return render_template(
        'game_detail.html', game=game, is_admin=admin_required()
    )


@app.route('/games/new', methods=['GET', 'POST'])
@jwt_required()
def new_game_form():
    """Display and process the game creation form."""
    if not admin_required():
        abort(403)
    form = GameForm()
    if form.validate_on_submit():
        game = Game(
            name=form.name.data,
            description=form.description.data,
            genre=form.genre.data,
            release_date=form.release_date.data,
        )
        db.session.add(game)
        db.session.commit()
        return redirect(url_for('games_list'))
    return render_template('game_form.html', form=form, form_title='Nuevo juego')


@app.route('/games/edit/<int:gid>', methods=['GET', 'POST'])
@jwt_required()
def edit_game_form(gid):
    """Display and process the game edit form."""
    if not admin_required():
        abort(403)
    game = db.session.get(Game, gid) or abort(404)
    form = GameForm(obj=game)
    if form.validate_on_submit():
        form.populate_obj(game)
        db.session.commit()
        return redirect(url_for('games_list'))
    return render_template(
        'game_form.html', form=form, form_title='Editar juego')

@app.route('/games/<int:gid>', methods=['PUT'])
@jwt_required()
def update_game(gid):
    data = request.get_json() or {}
    game = db.session.get(Game, gid)
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
    return '', 404

@app.route('/games/<int:gid>', methods=['DELETE'])
@jwt_required()
def delete_game(gid):
    if not admin_required():
        return '', 403
    game = db.session.get(Game, gid)
    if game:
        db.session.delete(game)
        db.session.commit()
        return '', 204
    return '', 404

if __name__ == '__main__':
    debug_env = os.getenv('DEBUG', '')
    debug_mode = debug_env.lower() in ('1', 'true', 'yes')
    app.run(debug=debug_mode)
