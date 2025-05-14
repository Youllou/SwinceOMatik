from flask import Flask
from .config import Config
from .db import init_db
from .routes.swince_routes import swince_bp
from .routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    app.register_blueprint(swince_bp, url_prefix='/swince')
    app.register_blueprint(user_bp, url_prefix='/users')

    return app
