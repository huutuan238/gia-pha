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
    # from . import models
    from app.routes.family_tree import family_tree
    from app.routes.person import person_bp
    from app.routes.event import event_bp
    from app.routes.album import album_bp
    from app.routes.family import families_bp
    from app.routes.auth import auth_bp
    from app.routes.user import users_bp
    from app.routes.search import search_bp

    from flask_jwt_extended import JWTManager

    app.config["JWT_SECRET_KEY"] = "đổi-thành-chuỗi-bí-mật-thật-dài"
    JWTManager(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)

    app.register_blueprint(family_tree)
    app.register_blueprint(person_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(album_bp)
    app.register_blueprint(families_bp)
    app.register_blueprint(search_bp)

    return app
