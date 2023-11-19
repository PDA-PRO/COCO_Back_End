from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_signup():
    response = client.post("/signup",json={"name":"test","id":"test","pw":"test1234!","email":"test@dot.com"})
    assert response.status_code == 200
    assert response.json() == {"code": 1}

def test_login():
    response = client.post("/login",json={"username":"test","password":"test1234!"})

    assert response.status_code == 200
    assert response.json() == {"code": 0}