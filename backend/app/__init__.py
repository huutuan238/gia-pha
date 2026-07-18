from flask import Flask
from flask_cors import CORS

from .extensions import db, migrate
from config import Config


def create_app():

    app = Flask(__name__)

    # Load config
    app.config.from_object(Config)

    # Enable CORS cho VueJS
    CORS(app)

    # Init SQLAlchemy
    db.init_app(app)

    # Init Flask-Migrate
    migrate.init_app(app, db)

    # Import models để Alembic detect table
    from . import models
    from app.routes.person import person_bp
    
    app.register_blueprint(person_bp)

    return app