from flask import Blueprint, request, session, redirect, render_template

from models import db
from utils import login_required, import_csv

imprt = Blueprint("import", __name__)
FILE_DIR = "temp_files"


@imprt.route("/import", methods=["GET", "POST"])
@login_required
def import_csv_file():
    if request.method == "POST" and request.files["file"]:
        file = request.files["file"]
        if file.filename.endswith(".csv") and file:
            file_path = f"{FILE_DIR}/{session.get('user_id')}.csv"
            file.save(file_path, )
            import_csv(file_path, session.get("user_id"), db)
            return redirect("/")
        else:
            return render_template("import.html", msg="File must be a CSV file")
    return render_template("import.html")
