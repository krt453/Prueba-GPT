from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField
from wtforms.validators import DataRequired, Optional


class GameForm(FlaskForm):
    """Form to create or update a game."""

    name = StringField('Nombre', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[Optional()])
    genre = StringField('Género', validators=[Optional()])
    release_date = DateField('Fecha de lanzamiento', format='%Y-%m-%d', validators=[Optional()])
