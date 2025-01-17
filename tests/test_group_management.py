import pytest
from app import create_app
from app.config import Config

@pytest.fixture
def client():
    """Create a test client for the app."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client

def test_group_exists():
    """Test that groups are properly configured."""
    assert 'team1' in Config.ALLOWED_GROUPS
    assert 'password' in Config.ALLOWED_GROUPS['team1']
    assert Config.ALLOWED_GROUPS['team1']['password'] is not None

def test_group_name_format():
    """Test that group names follow the expected format."""
    for group_id in Config.ALLOWED_GROUPS:
        assert group_id.isalnum(), f"Group ID {group_id} should be alphanumeric"
        assert len(group_id) <= 20, f"Group ID {group_id} should not exceed 20 characters"

def test_group_password_security():
    """Test that group passwords meet security requirements."""
    for group_id, group_data in Config.ALLOWED_GROUPS.items():
        password = group_data['password']
        assert password is not None, f"Password for {group_id} should not be None"
        assert len(password) >= 8, f"Password for {group_id} should be at least 8 characters"

def test_group_unique_passwords():
    """Test that each group has a unique password."""
    passwords = [group['password'] for group in Config.ALLOWED_GROUPS.values()]
    assert len(passwords) == len(set(passwords)), "Each group should have a unique password"

def test_group_name_display():
    """Test that group display names are properly configured."""
    for group_data in Config.ALLOWED_GROUPS.values():
        assert 'name' in group_data, "Each group should have a display name"
        assert len(group_data['name']) > 0, "Display name should not be empty" 