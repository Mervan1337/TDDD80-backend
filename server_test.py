import tempfile
import pytest
import os
import server
import req

@pytest.fixture
def client():
    # Makes a temporary file
    db_fd, name = tempfile.mkstemp()
    # Configs a temporary database
    server.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./our.db'
    # Enables testing session
    server.app.config['TESTING'] = True
    # Makes an client for testing
    with server.app.test_client() as client:
        #  In our currently state we create in this context
        with server.app.app_context():
            # Creates all clients
            server.db.create_all()
        # returns all clients
        yield client

    # Close our temporary tester
    os.close(db_fd)
    os.unlink(name)

import requests
url = "http://127.0.0.1:5000/"


def login_user(email ,password):
    rreq = requests.post(url+"login", json={"password":password,"email":email})
    print(rreq.json())
    token = rreq.json()['access-token']
    header = {"Authorization": "Bearer " + token}
    print(rreq.json())
    print(token)
    return header

def test_reg_user(client):
    status = client.post("/register", json={"username":"ellemannen","password":"password","email":"ellemannen@gmail.com"})
    assert status.status_code == 200 or status.status_code == 404, "assuming we made a correctly user"
    status = client.post("/register", json={"username": "ellemannen", "password": "password", "email": "ellemannen1@gmail.com"})
    assert status.status_code == status.status_code == 404, "Here we already made this username"

def test_login_user(client):
    status = client.post("/login", json={"password":"password","email":"ellemannen49@gmail.com"})
    assert status.status_code == 400, "an invalid login"
    status = client.post("/login", json={"password":"passwor111d","email":"ellemannen@gmail.com"})
    assert status.status_code == 400, "another invalid login"
    status = client.post("/login", json={"password": "password", "email": "ellemannen@gmail.com"})
    assert status.status_code == 200, "a valid login"

def test_logout_user(client):
    status = client.post("/login", json={"password": "0066", "email": "k13@gmail.com"})
    token = status.json['access-token']
    h1 = {"Authorization": "Bearer " + token}
    status = client.post("/logout", headers=h1)
    assert status.status_code == 200, "valid logout"
    client.post("/login", json={"password":"password","email":"ellemannen@gmail.com"})


def test_look_profile(client):
    status = client.post("/login", json={"password": "0066", "email": "k13@gmail.com"})
    token = status.json['access-token']
    h1 = {"Authorization": "Bearer " + token}
    status = client.post("/profile", headers=h1)
    assert status.status_code == 200, "check if profile gotten"


def test_like_user(client):
    status = client.post("/login", json={"password": "0066", "email": "k13@gmail.com"})
    token = status.json['access-token']
    h1 = {"Authorization": "Bearer " + token}
    status = client.post("/user/like", headers=h1, json={"target":"ellemannen"})
    assert status.status_code == 200 or 400, "A valid like"
    status = client.post(url + "user/like", headers=h1, json={"target": "eemannen"})
    assert status.status_code == 400, "A invalid like"


#  pytest --cov-report term --cov=server server_test.py