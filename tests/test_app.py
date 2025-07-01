import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app
from gamehub.models import User

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def register(client, username="user", password="pass", role="user"):
    return client.post(
        "/register", json={"username": username, "password": password, "role": role}
    )

def login(client, username="admin", password="secret"):
    resp = client.post("/login", json={"username": username, "password": password})
    if resp.status_code == 200:
        return resp.get_json()["access_token"]
    return None

def test_successful_login(client):
    resp = client.post("/login", json={"username": "admin", "password": "secret"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()

def test_failed_login(client):
    resp = client.post("/login", json={"username": "admin", "password": "bad"})
    assert resp.status_code == 401


def test_password_is_hashed(client):
    register(client, "alice", "mypw", "user")
    with client.application.app_context():
        user = User.query.filter_by(username="alice").first()
        assert user.password != "mypw"


def test_role_restrictions(client):
    # register a normal user and login
    register(client, "bob", "pw", "user")
    token = login(client, "bob", "pw")
    headers = {"Authorization": f"Bearer {token}"}
    # normal users cannot create games
    r = client.post(
        "/games",
        json={"name": "X", "description": "desc", "release_date": "2025-01-01"},
        headers=headers,
    )
    assert r.status_code == 403
    # admin can create
    admin_token = login(client)
    r = client.post(
        "/games",
        json={
            "name": "Z",
            "description": "d",
            "release_date": "2025-01-01",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert r.status_code == 201


def test_crud_flow(client):
    with client:
        token = login(client)
        headers = {"Authorization": f"Bearer {token}"}
        # create
        r = client.post(
            "/games",
            json={
                "name": "Tetris",
                "genre": "Puzzle",
                "description": "Desc",
                "release_date": "1984-06-06",
            },
            headers=headers,
        )
        assert r.status_code == 201
        game = r.get_json()
        gid = game["id"]
        # read
        r = client.get(f"/games/{gid}", headers=headers)
        assert r.status_code == 200
        assert r.get_json()["name"] == "Tetris"
        assert r.get_json()["genre"] == "Puzzle"
        assert r.get_json()["description"] == "Desc"
        assert r.get_json()["release_date"] == "1984-06-06"
        # update
        r = client.put(
            f"/games/{gid}",
            json={
                "name": "New Tetris",
                "genre": "Action",
                "description": "New",
                "release_date": "1985-01-01",
            },
            headers=headers,
        )
        assert r.status_code == 200
        assert r.get_json()["name"] == "New Tetris"
        assert r.get_json()["genre"] == "Action"
        assert r.get_json()["description"] == "New"
        assert r.get_json()["release_date"] == "1985-01-01"
        # delete
        r = client.delete(f"/games/{gid}", headers=headers)
        assert r.status_code == 204
        # confirm gone
        r = client.get(f"/games/{gid}", headers=headers)
        assert r.status_code == 404


def test_requires_auth(client):
    # create should fail without token
    r = client.post(
        "/games",
        json={"name": "X", "genre": "Y", "description": "d", "release_date": "2025-01-01"},
    )
    assert r.status_code == 401
    # update/delete should fail without token
    r = client.put("/games/1", json={"name": "foo"})
    assert r.status_code == 401
    r = client.delete("/games/1")
    assert r.status_code == 401


def test_search_games(client):
    token = login(client)
    headers = {"Authorization": f"Bearer {token}"}
    client.post(
        "/games",
        json={"name": "Tetris", "genre": "Puzzle"},
        headers=headers,
    )
    client.post(
        "/games",
        json={"name": "Doom", "genre": "Action"},
        headers=headers,
    )
    r = client.get("/games/search?q=tet", headers=headers)
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Tetris"
