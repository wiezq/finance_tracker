from flask import Blueprint, render_template, request, session
from models import Note, Income, Budget
from utils import login_required, calculate_balance, calculate_budget_spending

menus = Blueprint('routes', __name__)


@menus.route('/menu/', defaults={'msg': None})
@menus.route('/menu/<string:msg>')
@login_required
def menu(msg):
    notes_page, income_page = get_pages()
    notes, incomes = get_notes_and_incomes(notes_page, income_page)
    budget, total_amount, spent_within_budget_dates = get_budget_and_totals()
    format_dates(notes, incomes, budget)
    return render_template('index.html', msg=msg, notes=notes, incomes=incomes,
                           total_amount=total_amount, budget=budget, spent_within_budget=spent_within_budget_dates)


def get_pages():
    notes_page = request.args.get('notes_page', 1, type=int)
    income_page = request.args.get('income_page', 1, type=int)
    return notes_page, income_page


def get_notes_and_incomes(notes_page, income_page):
    notes = Note.query.filter_by(user_id=session.get("user_id")).order_by(Note.date.desc()).paginate(page=notes_page,
                                                                                                     per_page=5)
    incomes = Income.query.filter_by(user_id=session.get("user_id")).order_by(Income.date.desc()).paginate(
        page=income_page, per_page=5)
    return notes, incomes


def get_budget_and_totals():
    budget = Budget.query.filter_by(user_id=session.get("user_id")).first()
    balance = calculate_balance()
    on_budget_spending = None
    if budget is not None:
        on_budget_spending = calculate_budget_spending()
    return budget, balance, on_budget_spending


def format_dates(notes, incomes, budget):

    for note in notes.items:
        note.date = note.date.strftime('%d-%m-%Y')
    for income in incomes.items:
        income.date = income.date.strftime('%d-%m-%Y')
    if budget is not None:
        budget.date_from = budget.date_from.strftime('%d-%m-%Y')
        budget.date_to = budget.date_to.strftime('%d-%m-%Y')
