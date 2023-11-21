import io
from datetime import datetime
from functools import wraps
from werkzeug.exceptions import NotFound
from flask import Flask, Response, request, render_template, session, redirect, url_for
from flask_session import Session
from config import AppConfig
from models import db, Note, User, Income, Budget
from plotter import plot_chart
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from utils import import_csv

# CONFIG
# TODO: reorganise here
app = Flask(__name__)
FILE_DIR = "temp_files"
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


@app.errorhandler(NotFound)
def handle_not_found(error):
    return redirect("/menu")


@app.route("/import", methods=["GET", "POST"])
@login_required
def import_csv_file():
    if request.method == "POST" and request.files["file"]:
        file = request.files["file"]
        if file.filename.endswith(".csv"):
            file_path = f"{FILE_DIR}/{session.get('user_id')}.csv"
            file.save(file_path, )
            import_csv(file_path, session.get("user_id"), db)
            return redirect("/")
        else:
            return render_template("import.html", msg="File must be a CSV file")
    return render_template("import.html")


@app.route('/plot/<string:start_date>/<string:end_date>/<string:chart_type>.png', methods=['GET'])
@login_required
def get_chart(chart_type, start_date, end_date):
    # Convert the string dates to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Fetch notes between the start_date and end_date
    notes = Note.query.filter(Note.user_id == session.get("user_id"), Note.date >= start_date,
                              Note.date <= end_date).all()

    fig = plot_chart(chart_type, notes)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/statistic', methods=["GET", "POST"])
@login_required
def statistic():
    if request.method == "POST" and request.form["start_date"] and request.form["end_date"]:
        start_date = datetime.strptime(request.form["start_date"], '%Y-%m-%d')
        end_date = datetime.strptime(request.form["end_date"], '%Y-%m-%d')
        notes_between_dates = Note.query.filter(Note.user_id == session.get("user_id"), Note.date >= start_date,
                                                Note.date <= end_date).all()

        if len(notes_between_dates) > 0:
            start_date = str(start_date).split(" ")[0]
            end_date = str(end_date).split(" ")[0]
            return render_template("statistic.html", start_date=start_date, end_date=end_date)
        else:
            return render_template("statistic.html", start_date=None, end_date=None, msg="No notes found")

    return render_template("statistic.html", start_date=None, end_date=None)


def get_total_amount(notes, incomes):
    total_amount = 0
    for income in incomes:
        total_amount += income.amount
    for note in notes:
        total_amount -= note.amount
    return total_amount


def get_spend_within_budget(notes, budget):
    date_from = budget.date_from
    date_to = budget.date_to
    total_spend = 0
    for note in notes:
        if date_from <= note.date <= date_to:
            total_spend += note.amount
    return total_spend


@app.route('/menu/', defaults={'msg': None})
@app.route('/menu/<string:msg>')
@login_required
def menu(msg):
    # Get page number from query parameter (default to 1 if not present)
    notes_page = request.args.get('notes_page', 1, type=int)
    income_page = request.args.get('income_page', 1, type=int)

    # Get notes and incomes for the current page
    notes = Note.query.filter_by(user_id=session.get("user_id")).order_by(Note.date.desc()).paginate(page=notes_page,
                                                                                                     per_page=5)
    incomes = Income.query.filter_by(user_id=session.get("user_id")).order_by(Income.date.desc()).paginate(
        page=income_page, per_page=5)

    budget = Budget.query.filter_by(user_id=session.get("user_id")).first()
    total_amount = get_total_amount(notes.items, incomes.items)
    spent_within_budget_dates = get_spend_within_budget(notes, budget)

    for note in notes.items:
        note.date = note.date.strftime('%d-%m-%Y')

    for income in incomes.items:
        income.date = income.date.strftime('%d-%m-%Y')

    budget.date_from = budget.date_from.strftime('%d-%m-%Y')
    budget.date_to = budget.date_to.strftime('%d-%m-%Y')
    return render_template('index.html', msg=msg, notes=notes, incomes=incomes,
                           total_amount=total_amount, budget=budget, spent_within_budget=spent_within_budget_dates)


@app.route('/budget', methods=["GET"])
def render_budget():
    budget = Budget.query.filter_by(user_id=session.get("user_id")).first()
    return render_template("budget.html", msg=None, budget=budget)


@login_required
@app.route('/save_budget', methods=['POST'])
def save_budget():
    if request.form["amount"] and request.form["date_from"] and request.form["date_to"]:
        if Budget.query.filter_by(user_id=session.get("user_id")).first() is not None:
            budget = Budget.query.filter_by(user_id=session.get("user_id")).first()
            return render_template("budget.html", msg="You already have a budget", budget=budget)
        user_id = session.get("user_id")
        amount = request.form["amount"]
        date_from = request.form["date_from"]
        date_to = request.form["date_to"]
        date_from = datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.strptime(date_to, '%Y-%m-%d')
        new_note = Budget(amount=amount,
                          date_from=date_from,
                          date_to=date_to,
                          user_id=user_id)
        db.session.add(new_note)
        db.session.commit()
    return redirect("/")


@login_required
@app.route('/delete/<int:id>', methods=['GET'])
def delete_note(id):
    if id:
        user_id = session.get("user_id")
        note = Note.query.filter_by(id=id, user_id=user_id).delete()
        db.session.commit()
    return redirect('/')


@login_required
@app.route('/save_expenses', methods=['POST'])
def save_note():
    if request.form["category"] and request.form["amount"] and request.form["date"]:
        notes = Note.query.filter_by(user_id=session.get("user_id")).all()
        income = Income.query.filter_by(user_id=session.get("user_id")).all()
        total_amount = get_total_amount(notes=notes, incomes=income)
        if total_amount - int(request.form["amount"]) < 0:
            return redirect(f"/menu/You don't have enough money to spend")

        user_id = session.get("user_id")
        type = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        date = datetime.strptime(date, '%Y-%m-%d')
        description = request.form["description"]
        new_note = Note(type=type,
                        amount=amount,
                        date=date,
                        user_id=user_id,
                        description=description)
        db.session.add(new_note)
        db.session.commit()
    return redirect("/")


@login_required
@app.route('/save_income', methods=['POST'])
def save_income():
    if request.form["category"] and request.form["amount"] and request.form["date"]:
        user_id = session.get("user_id")
        type = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]
        date = datetime.strptime(date, '%Y-%m-%d')
        description = request.form["description"]
        new_note = Income(type=type,
                          amount=amount,
                          date=date,
                          user_id=user_id,
                          description=description)
        db.session.add(new_note)
        db.session.commit()
    return redirect("/")


# @app.route("/import_csv", methods=["GET"])
# @login_required
# def importCsv():
#     import_csv("data.csv", session.get("user_id"), db)
#     return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get("user_id") is not None:
        return redirect("/")

    if request.method == "POST" and request.form['email'] and request.form['username'] and request.form['password']:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

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
    if session.get("user_id") is not None:
        return redirect("/")
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
    session.pop("user_id", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
