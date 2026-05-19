import pytest
from app import app

@pytest.fixture
def client():
    # Flask ko testing mode mein daalein
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_page(client):
    """Test if the main template loads successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_status_api_invalid_video(client):
    """Test status API for a video that doesn't exist"""
    response = client.get('/api/status/invalid_id_123')
    assert response.status_code == 200
    assert response.get_json()["exists"] == False

def test_process_api_no_url(client):
    """Test process API behavior when no URL is provided"""
    response = client.post('/api/process', json={})
    assert response.status_code == 400
    assert response.get_json()["success"] == False