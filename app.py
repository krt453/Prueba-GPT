from flask import Flask
from flask_caching import Cache

app = Flask(__name__)
app.config.from_mapping({
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_HOST": "localhost",
    "CACHE_REDIS_PORT": 6379,
})
cache = Cache(app)

@app.route('/')
@cache.cached(timeout=60)
def home():
    return '¡Bienvenido a Game Hub!'

if __name__ == '__main__':
    app.run()
