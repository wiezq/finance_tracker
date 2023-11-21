import os
from datetime import datetime

import pandas

from models import Note


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
