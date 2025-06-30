from . import app

@app.route('/')
def home():
    return '¡Bienvenido a Game Hub!'
