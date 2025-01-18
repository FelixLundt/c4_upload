import pytest
from flask import session
from app import create_app
from app.config import Config

@pytest.fixture
def client():
    """Create a test client for the app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        yield client

def test_login_page_loads(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_successful_login(client):
    """Test successful login with correct credentials."""
    response = client.post('/login', data={
        'group_name': 'team1',
        'password': Config.ALLOWED_GROUPS['team1']['password']
    }, follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess['group_name'] == 'team1'

def test_failed_login_wrong_password(client):
    """Test login failure with wrong password."""
    response = client.post('/login', data={
        'group_name': 'team1',
        'password': 'wrong_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid password' in response.data

def test_failed_login_invalid_group(client):
    """Test login failure with non-existent group."""
    response = client.post('/login', data={
        'group_name': 'nonexistent_team',
        'password': 'any_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid group ID' in response.data

def test_logout(client):
    """Test logout functionality."""
    # First login
    client.post('/login', data={
        'group_id': 'team1',
        'password': Config.ALLOWED_GROUPS['team1']['password']
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'group_name' not in sess 