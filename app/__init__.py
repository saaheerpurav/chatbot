from flask import Flask
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from .config import Config
from .models import db, Users

login_manager = LoginManager()
bcrypt = Bcrypt()

@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    bcrypt.init_app(app)

    from .routes import chatbot, auth

    app.register_blueprint(chatbot.bp)
    app.register_blueprint(auth.bp)

    return app