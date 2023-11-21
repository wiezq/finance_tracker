from datetime import datetime

from flask import render_template, session, request, redirect, Blueprint

from models import Budget, db
from utils import login_required

budget = Blueprint('budget', __name__)


@budget.route('/budget', methods=["GET"])
def render_budget():
    budget = get_budget()
    return render_template("budget.html", msg=None, budget=budget)


@login_required
@budget.route('/save_budget', methods=['POST'])
def save_budget():
    if validate_budget_form(request.form):
        budget = Budget.query.filter_by(user_id=session.get("user_id")).first()
        if budget is not None:
            return render_template("budget.html", msg="You already have a budget", budget=budget)
        save_new_budget(request.form)
    return redirect("/")


def get_budget():
    return Budget.query.filter_by(user_id=session.get("user_id")).first()


def validate_budget_form(form):
    return form["amount"] and form["date_from"] and form["date_to"]


def save_new_budget(form):
    user_id = session.get("user_id")
    amount = form["amount"]
    date_from = datetime.strptime(form["date_from"], '%Y-%m-%d')
    date_to = datetime.strptime(form["date_to"], '%Y-%m-%d')
    new_budget = Budget(amount=amount,
                        date_from=date_from,
                        date_to=date_to,
                        user_id=user_id)
    db.session.add(new_budget)
    db.session.commit()
