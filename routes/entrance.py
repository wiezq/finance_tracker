from flask import session, redirect, request, render_template, Blueprint
from flask_bcrypt import Bcrypt

from models import User, db
from utils import login_required

entrance = Blueprint('entrance', __name__)
bcrypt = Bcrypt()


@entrance.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("user_id") is not None:
        return redirect("/")
    if request.method == "POST" and validate_registration_form(request.form):
        return handle_registration(request.form)
    return render_template("registration.html")


def validate_registration_form(form):
    return form['email'] and form['username'] and form['password']


def handle_registration(form):
    username = form['username']
    email = form['email']
    password = form['password']
    user_exists_email = User.query.filter_by(email=email).first() is not None
    user_exists_username = User.query.filter_by(username=username).first() is not None
    if user_exists_email or user_exists_username:
        return render_template("registration.html", msg='User already exists'), 401

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    session["user_id"] = new_user.id
    session["username"] = new_user.username
    session["email"] = new_user.email
    return redirect("/")


@entrance.route('/login', methods=['GET', 'POST'])
def login():
    if session.get("user_id") is not None:
        return redirect("/")
    if request.method == "POST" and validate_login_form(request.form):
        return handle_login(request.form)
    return render_template("login.html")


def validate_login_form(form):
    return form['email'] and form['password']


def handle_login(form):
    email = form['email']
    password = form['password']
    user = User.query.filter_by(email=email, password=password).first()
    if user and bcrypt.check_password_hash(user.password, password):
        session["user_id"] = user.id
        session["username"] = user.username
        session["email"] = user.email
        return redirect("/")
    return render_template("login.html", msg='User not found'), 401


@entrance.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.pop("user_id", None)
    return redirect("/")
