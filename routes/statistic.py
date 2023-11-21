import io
from datetime import datetime

from flask import Blueprint, session, Response, request, render_template
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from models import Note
from plotter import plot_chart
from utils import login_required

statistics = Blueprint('statistics', __name__)


@statistics.route('/plot/<string:start_date>/<string:end_date>/<string:chart_type>.png', methods=['GET'])
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


@statistics.route('/statistic', methods=["GET", "POST"])
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
