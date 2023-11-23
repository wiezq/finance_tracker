from flask import Flask

from config import AppConfig
from flask_session import Session
from models import db

from routes.budget import budget
from routes.entrance import entrance, bcrypt
from routes.imprt import imprt
from routes.income import income
from routes.menu import menus
from routes.note import note
from routes.statistic import statistics

from routes.handlers.ErrorHandler import handler

# CONFIG

# Init app
app = Flask(__name__)

# Config import
app.config.from_object(AppConfig)

# Blueprints
app.register_blueprint(budget)
app.register_blueprint(imprt)
app.register_blueprint(statistics)
app.register_blueprint(entrance)
app.register_blueprint(note)
app.register_blueprint(income)
app.register_blueprint(menus)
app.register_blueprint(handler)

# Init bcrypt
bcrypt.init_app(app)

# Init session
Session(app)

# Init db
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
