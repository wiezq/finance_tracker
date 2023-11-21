from datetime import datetime

from flask import Blueprint, request, session, redirect

from models import Income, db
from utils import login_required

income = Blueprint('income', __name__)


@login_required
@income.route('/save_income', methods=['POST'])
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