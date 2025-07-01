"""Database models for Game Hub."""

from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy database instance
# The application will call ``db.init_app(app)`` during setup.
db = SQLAlchemy()

class Game(db.Model):
    """Game model representing a single game entry."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    genre = db.Column(db.String(80), nullable=True)
    release_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "genre": self.genre,
            "release_date": self.release_date.isoformat() if self.release_date else None,
        }


class User(db.Model):
    """Simple user account with role support."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="user", nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
        }
