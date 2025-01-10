from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Configure app
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_EXTENSIONS'] = ['.py', '.txt']
    
    # Register routes
    from app.routes import upload
    app.register_blueprint(upload.bp)
    
    return app 