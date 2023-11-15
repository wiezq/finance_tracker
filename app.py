from uuid import uuid4
from datetime import datetime
from flask import Flask, render_template, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
# The Session instance is not used for direct access, you should always use flask.session
from flask_session import Session

# CONFIG
app = Flask(__name__)
app.config['SECRET_KEY'] = "asdasdas"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://db_user:db_user_pass@localhost:6033/app_db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Session(app)

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


db.init_app(app)

with app.app_context():
    db.create_all()


# ROUTES
@app.route("/", methods=["GET"])
def menu():
    msg = ''
    if not session.get("user_id"):
        return redirect("/login")
    notes = Note.query.filter_by(user_id=session.get("user_id")).all()
    return render_template('index.html', msg=msg, notes=notes)


@app.route("/save", methods=["POST"])
def save():
    if request.form["category"] and request.form["amount"] and request.form["date"]:
        user_id = session.get("user_id")
        type = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        date = datetime.strptime(date, '%Y-%m-%d')
        new_note = Note(type=type,
                        amount=amount,
                        date=date,
                        user_id=user_id)
        db.session.add(new_note)
        db.session.commit()
        print("New note added")

    print(request.form["category"])
    print(request.form["amount"])
    print(request.form["date"])
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST" and request.form['email'] and request.form['username'] and request.form['password']:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        print(username, email, password)

        user_exists = User.query.filter_by(email=email).first() is not None

        if user_exists:
            return render_template("registration.html", msg='User already exists'), 401

        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        session["user_id"] = new_user.id
        return redirect("/registration.html")

    return render_template("registration.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST" and request.form['email'] and request.form['password']:

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()

        if user is None:
            return render_template("login.html", msg='User not found'), 401

        session["user_id"] = user.id
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
