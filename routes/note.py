import sys
from datetime import datetime

from flask import Blueprint, session, redirect, request

from models import Note, db, Income
from utils import login_required, calculate_balance

note = Blueprint('note', __name__)


@login_required
@note.route('/delete_note/<int:note_id>', methods=['GET'])
def delete_note(note_id):
    if note_id:
        delete_note_by_id(note_id)
    return redirect('/')


@login_required
@note.route('/save_expenses', methods=['POST'])
def save_note():
    if validate_form(request.form):
        save_new_note(request.form)
    else:
        return redirect("/menu/Invalid form data")
    return redirect("/")


def delete_note_by_id(note_id):
    user_id = session.get("user_id")
    Note.query.filter_by(id=note_id, user_id=user_id).delete()
    db.session.commit()


def validate_form(form):
    if form["category"] and form["amount"] and form["date"]:
        if form["amount"].isdigit() and 0 < int(form["amount"]) <= sys.maxsize:
            return True

    return False


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
