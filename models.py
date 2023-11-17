from uuid import uuid4
from sqlalchemy import DateTime
from flask_sqlalchemy import SQLAlchemy

# DB INIT
db = SQLAlchemy()


def get_uuid():
    return uuid4().hex


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    username = db.Column(db.String(18), unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    notes = db.relationship('Note', backref='user', lazy=True)


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(DateTime, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)