from flask import Flask

app = Flask(__name__)
app.config.from_object('gamehub.config.Config')

from . import routes  # noqa: E402
