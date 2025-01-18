from flask import Flask
from app.config import Config


def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)
    
    # Register routes
    from app.routes import upload, auth, home
    app.register_blueprint(upload.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(home.bp)
    
    # Make home page the default route
    app.add_url_rule('/', endpoint='home.index')
    
    return app 