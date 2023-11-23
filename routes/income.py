import sys
from datetime import datetime

from flask import Blueprint, request, session, redirect

from models import Income, db
from utils import login_required

income = Blueprint('income', __name__)


def validate_income_form(form):
    if form['category'] and form['amount'] and form['date']:
        if form['amount'].isdigit() and 0 < int(form['amount']) <= sys.maxsize:
            return True
    return False


@login_required
@income.route('/save_income', methods=['POST'])
def save_income():
    if validate_income_form(request.form):
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
    else:
        redirect("/menu/Ivalid income form")

    return redirect("/")


@login_required
@income.route('/delete_income/<int:income_id>', methods=['GET'])
def delete_income(income_id):
    if income_id:
        Income.query.filter_by(id=income_id, user_id=session.get("user_id")).delete()
        db.session.commit()
    return redirect('/')
