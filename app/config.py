import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '../.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'une-cle-secrete-tres-secure'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY') or 'super-secret-jwt-key'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'mysql+pymysql://duchesse:Passer123@localhost/systemdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(basedir, 'sessions')
    FACE_DATA_PATH = os.path.join(basedir, 'static/faces')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 heure