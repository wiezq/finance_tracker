from datetime import datetime

from flask import Blueprint, session, redirect, request

from models import Note, db, Income
from utils import login_required, calculate_balance

note = Blueprint('note', __name__)


@login_required
@note.route('/delete/<int:note_id>', methods=['GET'])
def delete_note(note_id):
    if note_id:
        delete_note_by_id(note_id)
    return redirect('/')


@login_required
@note.route('/save_expenses', methods=['POST'])
def save_note():
    if validate_form(request.form):

        notes = Note.query.filter_by(user_id=session.get("user_id")).all()
        income = Income.query.filter_by(user_id=session.get("user_id")).all()

        balance = calculate_balance(notes=notes, incomes=income)
        expense_amount = int(request.form["amount"])
        if balance - expense_amount < 0:
            return redirect(f"/menu/You don't have enough money to spend")
        save_new_note(request.form)
    return redirect("/")


def delete_note_by_id(note_id):
    user_id = session.get("user_id")
    Note.query.filter_by(id=note_id, user_id=user_id).delete()
    db.session.commit()


def validate_form(form):
    return form["category"] and form["amount"] and form["date"]


def save_new_note(form):
    user_id = session.get("user_id")
    type = form["category"]
    amount = form["amount"]
    date = datetime.strptime(form["date"], '%Y-%m-%d')
    description = form["description"]
    new_note = Note(type=type,
                    amount=amount,
                    date=date,
                    user_id=user_id,
                    description=description)
    db.session.add(new_note)
    db.session.commit()
