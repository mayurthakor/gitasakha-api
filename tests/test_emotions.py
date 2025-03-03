import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_emotions(client):
    response = client.get('/v1/emotions')
    assert response.status_code == 200
    assert 'emotions' in response.json

def test_get_emotion_detail(client):
    response = client.get('/v1/emotions/joy')
    assert response.status_code == 200
    assert 'name' in response.json
    assert 'themes' in response.json

def test_get_theme_shloks(client):
    response = client.get('/v1/emotions/joy/themes/true_happiness')
    assert response.status_code == 200
    assert 'shloks' in response.json

def test_get_shlok(client):
    response = client.get('/v1/shloks/2/38')
    assert response.status_code == 200
    assert 'chapter' in response.json
    assert 'verse' in response.json

def test_search_shloks(client):
    response = client.get('/v1/search?query=happiness')
    assert response.status_code == 200
    assert 'results' in response.json
