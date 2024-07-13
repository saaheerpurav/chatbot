from flask import Flask, cli
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    #cli.load_dotenv()

    app.config.from_object(config_class)
    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    return app