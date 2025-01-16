import os
from pathlib import Path

# Get the webapp root directory (where .env is located)
WEBAPP_ROOT = Path(__file__).parent.parent

class Config:
    # Flask settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.zip']
    
    # Google Cloud Storage settings
    STORAGE_BUCKET = 'c4league'
    STORAGE_KEY_PATH = os.environ.get(
        'GOOGLE_APPLICATION_CREDENTIALS',
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'connect4-service-key.json')
    )

    # Validator settings
    # In development: '../c4utils' relative to webapp root
    # In deployment: '.' (current directory)
    VALIDATOR_PATH = str(WEBAPP_ROOT / os.environ.get('C4UTILS_PATH', '../c4utils'))

    # Group settings
    ALLOWED_GROUPS = {
        'team1': {
            'name': 'Team 1',
            'password': os.environ.get('TEAM1_PASSWORD')
        },
        'team2': {
            'name': 'Team 2',
            'password': os.environ.get('TEAM2_PASSWORD')
        }
    }
 
    # You can add more configuration sections as needed:
    # Tournament settings, etc. 