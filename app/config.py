import os
import dotenv

class Config:
    dotenv.load_dotenv()

    ENV = "prod" #  SET dev OR prod
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False