import zipfile
from io import BytesIO
import importlib.util
import sys
from typing import Dict, Any
import tempfile
from flask import current_app

def validate_submission(zip_content: bytes) -> Dict[str, Any]:
    """
    Validates a zipped submission by checking:
    1. Required files and structure
    2. Python package validity
    3. generate_move function existence and game interface compliance
    """
    # Initialize validator
    try:
        c4utils_path = current_app.config.get('VALIDATOR_PATH', '../c4utils')
        sys.path.insert(0, c4utils_path)
        connect4_validator = importlib.import_module('c4utils.agent_interface')
        sys.path.remove(c4utils_path)
    except ImportError:
        return {
            'valid': False,
            'message': 'Game validator package not installed. Please install c4utils package.'
        }
    except UnboundLocalError:
        return {
            'valid': False,
            'message': 'Game validator package not installed. Could not find c4utils package.'
        }
    except Exception as e:
        return {
            'valid': False,
            'message': f'Unknown validation error: {str(e)}'
        }
            

    # Rest of validation code using connect4_validator
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract ZIP contents
            zip_bytes = BytesIO(zip_content)
            with zipfile.ZipFile(zip_bytes) as z:
                # Check for requirements.txt at root level
                files = z.namelist()
                if 'requirements.txt' not in files:
                    return {
                        'valid': False,
                        'message': 'requirements.txt must be in the root of the ZIP'
                    }
                
                # Check for agent package
                if not any(f.startswith('agent/') for f in files):
                    return {
                        'valid': False,
                        'message': 'ZIP must contain an "agent" package directory'
                    }
                
                # Check for __init__.py in agent package
                if 'agent/__init__.py' not in files:
                    return {
                        'valid': False,
                        'message': 'agent package must contain __init__.py'
                    }
                
                # Extract files for further validation
                z.extractall(temp_dir)
                
                # Try to import the agent package
                try:
                    sys.path.insert(0, temp_dir)
                    agent_module = importlib.import_module('agent')
                    
                    # Basic function checks
                    if not hasattr(agent_module, 'generate_move'):
                        return {
                            'valid': False,
                            'message': 'agent package must expose a generate_move function'
                        }
                    
                    if not callable(agent_module.generate_move):
                        return {
                            'valid': False,
                            'message': 'generate_move must be a callable function'
                        }
                    
                    # Validate against game interface
                    valid, error = connect4_validator.validate_agent_function(agent_module.generate_move)
                    if error is not None:
                        return {
                            'valid': False,
                            'message': f'Game validation failed: {str(error)}'
                        }
                    if not valid:  # If result is False
                        return {
                            'valid': False,
                            'message': 'Agent failed game interface validation (invalid moves returned)'
                        }
                    
                except ImportError as e:
                    return {
                        'valid': False,
                        'message': f'Failed to import agent package: {str(e)}'
                    }
                finally:
                    sys.path.pop(0)
                
        except zipfile.BadZipFile:
            return {
                'valid': False,
                'message': 'Invalid ZIP file'
            }
        except Exception as e:
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }
    
    return {
        'valid': True,
        'message': 'Validation successful'
    } 