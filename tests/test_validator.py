import zipfile
import pytest
from io import BytesIO
from app.validator import validate_submission

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

def test_valid_submission(valid_submission):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in valid_submission.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is True
    assert result['message'] == "Validation successful"

def test_missing_requirements(missing_requirements):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in missing_requirements.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is False
    assert "requirements.txt" in result['message']

def test_agent_module_instead_of_package(agent_module_instead_of_package):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in agent_module_instead_of_package.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is False
    assert "\"agent\" package directory" in result['message']

def test_missing_generate_move_function(missing_generate_move_function):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in missing_generate_move_function.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is False
    assert "generate_move function" in result['message']

def test_invalid_move(invalid_move):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in invalid_move.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is False
    assert "invalid move" in result['message']

def test_syntax_error(syntax_error):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in syntax_error.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is False
    assert "Validation error" in result['message']

def test_wrong_interface(wrong_interface):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w') as zf:
        for fpath, content in wrong_interface.items():
            zf.writestr(fpath, content)
    result = validate_submission(memory_zip.getvalue())
    assert result['valid'] is False
    assert all(message_part in result['message'] for 
               message_part in ["Game validation failed:",
                             "takes 1 positional argument",
                             "but 3 were given"])