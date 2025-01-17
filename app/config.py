import os
from pathlib import Path
from dotenv import load_dotenv
# Get the webapp root directory (where .env is located)
WEBAPP_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_EXTENSIONS = ['.zip']
    
    # Google Cloud Storage settings
    STORAGE_BUCKET = 'c4league'
    # In development, use service key file; in production, use default credentials
    STORAGE_KEY_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') if not os.getenv('GAE_ENV', '').startswith('standard') else None

    # Validator settings
    # Only used in development to find c4utils package
    VALIDATOR_PATH = str(WEBAPP_ROOT / os.environ.get('C4UTILS_PATH', '../c4utils')) if not os.getenv('GAE_ENV', '').startswith('standard') else None

    # Group settings
    ALLOWED_GROUPS = {
        os.environ.get('TEAM1_ID'): {
            'name': os.environ.get('TEAM1_NAME'),
            'password': os.environ.get('TEAM1_PASSWORD')
        },
        os.environ.get('TEAM2_ID'): {
            'name': os.environ.get('TEAM2_NAME'),
            'password': os.environ.get('TEAM2_PASSWORD')
        }
    }
 
    DOMAIN = os.environ.get('DOMAIN', 'localhost')  # Default to 'localhost' if not set 

    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')