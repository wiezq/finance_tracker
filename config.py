class AppConfig:
    SECRET_KEY = "asdasdas"
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://db_user:db_user_pass@localhost:6033/app_db'
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
