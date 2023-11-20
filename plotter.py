import calendar

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from models import Note
from flask import session
from collections import defaultdict


def plot_chart(chart_type, notes):
    if chart_type == "piechart":
        return plot_pie_chart_by_categories(notes)
    elif chart_type == "category_chart":
        return plot_chart_by_categories(notes)
    elif chart_type == "weekday_chart":
        return plot_bar_chart_by_day(notes)
    elif chart_type == "month_chart":
        return plot_bar_chart_by_month(notes)


def plot_bar_chart_by_month(notes):
    totals = defaultdict(int)
    for note in notes:
        totals[note.date.month] += note.amount
    months = range(1, 13)
    months_total = [0] * 12
    for month in totals.keys():
        months_total[month - 1] = totals[month]

    fig, ax = plt.subplots()
    ax.bar(months, months_total, tick_label=[calendar.month_name[m][:3] for m in months])
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Amount Spent (%)')
    return fig


def plot_bar_chart_by_day(notes):
    totals = defaultdict(int)
    total = 0
    for note in notes:
        total += note.amount
        totals[note.date.weekday()] += note.amount
    # days = list(totals.keys())
    days = [1, 2, 3, 4, 5, 6, 7]
    percents_in_days = []
    for day in days:
        percents_in_days.append(totals[day + 1] / total * 100)

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(days, percents_in_days)
    axis.set_xlabel('Day of the Week')
    axis.set_ylabel('Total Amount Spent')
    return fig


def plot_chart_by_categories(notes):
    totals = defaultdict(int)
    for note in notes:
        totals[note.type] += note.amount

    # Sort categories by total amount spent
    categories = sorted(totals, key=totals.get, reverse=True)
    amounts = [totals[category] for category in categories]

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    bars = axis.bar(categories, amounts)

    # Add data labels
    for bar in bars:
        yval = bar.get_height()
        axis.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom')  # va: vertical alignment

    axis.set_xlabel('Category')
    axis.set_ylabel('Total Amount Spent')
    axis.set_title('Spending by Category')


    return fig


def calculate_step_size(amounts):
    amount_range = max(amounts) - min(amounts)
    base_step_size = 100
    return base_step_size * (amount_range / 1000)


def plot_pie_chart_by_categories(notes):
    totals = defaultdict(int)
    total = 0
    for note in notes:
        total += note.amount
        totals[note.type] += note.amount
    categories = list(totals.keys())
    percents_in_categories = []
    for category in categories:
        category_total = totals[category]
        percents_in_categories.append(category_total / total * 100)

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.pie(percents_in_categories, labels=categories, autopct='%1.1f%%')
    return fig
