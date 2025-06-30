import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, username="admin", password="secret"):
    return client.post("/login", json={"username": username, "password": password})

def test_successful_login(client):
    response = login(client)
    assert response.status_code == 200
    assert response.get_json()["message"] == "logged in"

def test_failed_login(client):
    response = login(client, password="bad")
    assert response.status_code == 401


def test_crud_flow(client):
    with client:
        login(client)
        # create
        r = client.post("/games", json={"name": "Tetris", "genre": "Puzzle"})
        assert r.status_code == 201
        game = r.get_json()
        gid = game["id"]
        # read
        r = client.get(f"/games/{gid}")
        assert r.status_code == 200
        assert r.get_json()["name"] == "Tetris"
        # update
        r = client.put(f"/games/{gid}", json={"name": "New Tetris"})
        assert r.status_code == 200
        assert r.get_json()["name"] == "New Tetris"
        # delete
        r = client.delete(f"/games/{gid}")
        assert r.status_code == 204
        # confirm gone
        r = client.get(f"/games/{gid}")
        assert r.status_code == 404


def test_requires_auth(client):
    # create should fail without login
    r = client.post("/games", json={"name": "X", "genre": "Y"})
    assert r.status_code == 401
    # update/delete should fail without login
    r = client.put("/games/1", json={"name": "foo"})
    assert r.status_code == 401
    r = client.delete("/games/1")
    assert r.status_code == 401
