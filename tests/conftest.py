import pytest
import io
import zipfile
from app import create_app
from app.config import Config

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['STORAGE_BUCKET'] = 'test-bucket'
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """A test client that's already logged in."""
    client.post('/login', data={
        'group_id': 'team1',
        'password': Config.ALLOWED_GROUPS['team1']['password']
    })
    return client

@pytest.fixture
def sample_zip():
    """Create a sample zip file for testing."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        zip_file.writestr('agent.py', 'def generate_move(board): return 0')
    zip_buffer.seek(0)
    return zip_buffer 