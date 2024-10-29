# For handling csv-loaded data
import pandas as pd
import numpy as np
from app import db
from app.models import Course
from datetime import date

def import_courses(filename, user_id):
    col_types = {
        'name': str,
        'platform': str,
        'url': str,
        'instructor': str,
        'start': str,
        'complete': str,
        'content_hours': float,
        'has_cert': bool
    }
    data = pd.read_csv(f"imports/{filename}", dtype=col_types, index_col=False, header=0)

    for row in data.itertuples(index=False):
        # print(row.name)
        # print(row.platform)
        new_course = Course(
            name=row.name,
            platform=row.platform,
            url=row.url,
            instructor=row.instructor,
            start=pd.to_datetime(row.start),
            complete=pd.to_datetime(row.complete),
            content_hours=row.content_hours,
            has_cert=row.has_cert,
            date_added=date.today(),
            user_id=user_id
        )

        if row.complete:
            new_course.status = 'complete'

        elif row.start:
            new_course.status = 'in-progress'

        else:
            new_course.status = 'complete'

        # print(new_course.name)
        db.session.add(new_course)
        db.session.commit()
    # print(data.info())

    response_msg = "Course Import Successful"


    # name = data["name"]
    # start = data["start"]
    # has_cert = data["has_cert"]

    # print(data)
    # print(f"NAME: {name} TYPE: {type(name)}")
    # print(f"NAME: {start} TYPE: {type(start)}")
    # print(f"NAME: {has_cert} TYPE: {type(has_cert)}")

    print(response_msg)


import_courses("test_courses.csv", user_id=1)