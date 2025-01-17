import zipfile
import pytest
from io import BytesIO
from app.validator import validate_submission
from app import create_app

@pytest.fixture
def valid_submission():
    return {
        'requirements.txt': 'numpy\n',
        'agent/__init__.py': '''
import numpy as np
def generate_move(board, player, timeout):
    return np.int8(0) 
'''
    }

@pytest.fixture
def missing_requirements():
    return {
        'agent/__init__.py': '''
import numpy as np
def generate_move(board, player, timeout):
    return np.int8(0) 
'''
    }

@pytest.fixture
def agent_module_instead_of_package():
    return {
        'requirements.txt': 'numpy\n',
        'my_agent.py': 'def generate_move(board, player, timeout): return 0'
    }

@pytest.fixture
def missing_generate_move_function():
    return {
        'requirements.txt': 'numpy\n',
        'agent/__init__.py': '''
import numpy as np
def foo(board, player, timeout):
    return np.int8(0)
    '''
    }

@pytest.fixture
def invalid_move():
    return {
        'requirements.txt': '',
        'agent/__init__.py': '''
import numpy as np
def generate_move(board, player, timeout):
    return np.int8(9)  # Invalid column number
'''
    }

@pytest.fixture
def syntax_error():
    return {
        'requirements.txt': '',
        'agent/__init__.py': '''
def generate_move(board, player, timeout)
    return 0  # Missing colon after function definition
'''
    }

@pytest.fixture
def wrong_interface():
    return {
        'requirements.txt': '',
        'agent/__init__.py': '''
import numpy as np
def generate_move(wrong_params):
    return np.int8(0)
'''
    }

@pytest.fixture
def app():
    """Create test app with proper configuration."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['VALIDATOR_PATH'] = '../c4utils'
    return app

@pytest.fixture
def create_zip_submission():
    """Helper fixture to create zip files and ensure proper cleanup."""
    def _create_zip(submission_files):
        memory_zip = BytesIO()
        with zipfile.ZipFile(memory_zip, 'w') as zf:
            for fpath, content in submission_files.items():
                zf.writestr(fpath, content)
        zip_content = memory_zip.getvalue()
        memory_zip.close()  # Explicitly close the BytesIO object
        return zip_content
    return _create_zip

@pytest.fixture(autouse=True)
def reset_validator():
    """Reset any state before each test."""
    yield
    # Clean up any imported modules
    import sys
    modules_to_remove = [
        name for name in sys.modules 
        if name == 'agent' 
        or name.startswith('agent.')
    ]
    for module in modules_to_remove:
        del sys.modules[module]
    
    # Clean up any temporary files if they exist
    import shutil
    import os
    if os.path.exists('agent'):
        shutil.rmtree('agent')

def test_valid_submission(app, valid_submission, create_zip_submission):
    zip_content = create_zip_submission(valid_submission)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is True
        assert result['message'] == "Validation successful"

def test_missing_requirements(app, missing_requirements, create_zip_submission):
    zip_content = create_zip_submission(missing_requirements)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert "requirements.txt" in result['message']

def test_agent_module_instead_of_package(app, agent_module_instead_of_package, create_zip_submission):
    zip_content = create_zip_submission(agent_module_instead_of_package)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert "\"agent\" package directory" in result['message']

def test_missing_generate_move_function(app, missing_generate_move_function, create_zip_submission):
    zip_content = create_zip_submission(missing_generate_move_function)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert "generate_move function" in result['message']

def test_invalid_move(app, invalid_move, create_zip_submission):
    zip_content = create_zip_submission(invalid_move)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert "invalid move" in result['message']

def test_syntax_error(app, syntax_error, create_zip_submission):
    zip_content = create_zip_submission(syntax_error)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert "Validation error" in result['message']

def test_wrong_interface(app, wrong_interface, create_zip_submission):
    zip_content = create_zip_submission(wrong_interface)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert "Validation error" in result['message']

def test_wrong_interface(app, wrong_interface, create_zip_submission):
    zip_content = create_zip_submission(wrong_interface)
    with app.app_context():
        result = validate_submission(zip_content)
        assert result['valid'] is False
        assert all(message_part in result['message'] for 
                   message_part in ["Game validation failed:",
                                "takes 1 positional argument",
                                "but 3 were given"])