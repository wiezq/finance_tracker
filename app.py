import io
from datetime import datetime
from functools import wraps
from werkzeug.exceptions import NotFound
from flask import Flask, Response, request, render_template, session, redirect, url_for
from flask_session import Session
from config import AppConfig
from models import db, Note, User
from plotter import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from utils import import_csv

# CONFIG
# TODO: reorganise here
app = Flask(__name__)
app.config.from_object(AppConfig)
Session(app)
db.init_app(app)
with app.app_context():
    db.create_all()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# ROUTES
@app.errorhandler(NotFound)
def handle_not_found(error):
    return redirect("/")


@app.route('/<string:chart_type>.png', methods=['GET'])
@login_required
def get_pie_chart(chart_type):
    notes = Note.query.filter_by(user_id=session.get("user_id")).all()
    fig = plot_chart(chart_type, notes)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


# @app.route('/chart.png', methods=['GET'])
# @login_required
# def get_chart():
#     fig = plot_chart_by_categories()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')


@app.route('/', methods=["GET"])
@login_required
def menu():
    msg = ''

    # Get page number from query parameter (default to 1 if not present)
    page = request.args.get('page', 1, type=int)

    # Get notes for the current page
    notes = Note.query.filter_by(user_id=session.get("user_id")).paginate(page=page, per_page=5)
    for note in notes:
        note.date = note.date.strftime('%d-%m-%Y')
    return render_template('index.html', msg=msg, notes=notes)


@login_required
@app.route('/delete/<int:id>', methods=['GET'])
def delete_note(id):
    if id:
        user_id = session.get("user_id")
        note = Note.query.filter_by(id=id, user_id=user_id).delete()
        db.session.commit()
    return redirect('/')


@login_required
@app.route('/save', methods=['POST'])
def save_note():
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


# @app.route("/import_csv", methods=["GET"])
# @login_required
# def importCsv():
#     import_csv("data.csv", session.get("user_id"), db)
#     return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
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
        return redirect("/")

    return render_template("registration.html")


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session["user_id"] = None
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
