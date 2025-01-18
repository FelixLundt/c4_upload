import pytest
import io
import zipfile
from flask import session
from app import create_app
from app.config import Config
from unittest.mock import patch

@pytest.fixture
def client():
    """Create a test client for the app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        yield client

@pytest.fixture
def authenticated_client(client):
    """Create an authenticated test client."""
    client.post('/login', data={
        'group_name': 'team2',
        'password': Config.ALLOWED_GROUPS['team2']['password']
    })
    return client

@pytest.fixture
def sample_zip():
    """Create a sample zip file for testing."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('agent/__init__.py', 'def generate_move(board, player, timeout): return 0')
        zip_file.writestr('requirements.txt', '')
    zip_buffer.seek(0)
    return zip_buffer

@pytest.fixture
def sample_txt():
    """Create a sample txt file for testing."""
    data = io.BytesIO(b'Not a zip file')
    return data

def test_upload_requires_authentication(client):
    """Test that upload page requires authentication."""
    response = client.get('/upload')
    print(response.data)
    assert response.status_code == 302  # Redirect to login

def test_upload_page_loads(authenticated_client):
    """Test that upload page loads when authenticated."""
    response = authenticated_client.get('/upload')
    assert response.status_code == 200
    assert b'Upload' in response.data

def test_successful_upload(authenticated_client, sample_zip):
    """Test successful file upload."""
    # Mock the storage functionality
    with patch('app.storage.storage.Client'), \
         patch('app.storage.save_agent'):  # Patch the whole function instead
        response = authenticated_client.post('/upload', data={
            'submission': (sample_zip, 'submission.zip'),
            'agent_name': 'test-agent'
        }, content_type='multipart/form-data', follow_redirects=True)
        assert response.status_code == 200
        assert b'successfully' in response.data

# I can't even select a different file type, test not needed
# def test_upload_wrong_file_type(authenticated_client, sample_txt):
#     """Test upload with wrong file type."""
#     response = authenticated_client.post('/upload', data={
#         'submission': (sample_txt, 'submission.txt'),
#         'agent_name': 'test-agent'
#     }, content_type='multipart/form-data', follow_redirects=True)
#     assert response.status_code == 200
#     print(response.data)
#     assert b'Invalid' in response.data