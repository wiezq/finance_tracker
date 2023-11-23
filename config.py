import os


class AppConfig:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    # SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:password@localhost:3306/mydatabase'
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
