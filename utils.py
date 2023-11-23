import os
from datetime import datetime
from functools import wraps

import pandas
from flask import session, redirect, url_for

from models import Note, Budget, Income


def import_csv(file_name, user_id, db):
    csv_file = pandas.read_csv(file_name)
    for index, row in csv_file.iterrows():
        type = row["Category"]
        amount = int(row["Amount"])
        date = datetime.strptime(row["Date"], '%d-%m-%Y')
        new_note = Note(type=type,
                        amount=amount,
                        date=date,
                        user_id=user_id)
        db.session.add(new_note)
    db.session.commit()
    os.remove(file_name)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('entrance.login'))
        return f(*args, **kwargs)

    return decorated_function


def calculate_balance():
    notes = Note.query.filter_by(user_id=session.get("user_id")).all()
    incomes = Income.query.filter_by(user_id=session.get("user_id")).all()
    total_amount = 0
    for income in incomes:
        total_amount += income.amount
    for note in notes:
        total_amount -= note.amount
    return total_amount


def calculate_budget_spending():
    notes = Note.query.filter_by(user_id=session.get("user_id")).all()
    budget = Budget.query.filter_by(user_id=session.get("user_id")).first()
    date_from = budget.date_from
    date_to = budget.date_to
    total_spend = 0
    for note in notes:
        if date_from <= note.date <= date_to:
            total_spend += note.amount
    return total_spend
