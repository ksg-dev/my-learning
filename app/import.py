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
    data = pd.read_csv(f"imports/{filename}", dtype=col_types)

    for course in data:
        # new_course = Course(
        #     name=course["name"],
        #     platform=course["platform"],
        #     url=course["url"],
        #     instructor=course["instructor"],
        #     start=pd.to_datetime(course["start"]),
        #     complete=pd.to_datetime(course["complete"]),
        #     content_hours=course["content_hours"],
        #     has_cert=course["has_cert"],
        #     date_added=date.today(),
        #     user_id=user_id
        # )

        # if course["complete"]:
        #     new_course.status = 'complete'
        #
        # elif course["start"]:
        #     new_course.status = 'in-progress'
        #
        # else:
        #     new_course.status = 'complete'

        # db.session.add(new_course)
        # db.session.commit()

    # response_msg = "Course Import Successful"
    #     print(new_course)

    # name = data["name"]
    # start = data["start"]
    # has_cert = data["has_cert"]

    # print(data)
    # print(f"NAME: {name} TYPE: {type(name)}")
    # print(f"NAME: {start} TYPE: {type(start)}")
    # print(f"NAME: {has_cert} TYPE: {type(has_cert)}")

    # print(response_msg)


import_courses("test_courses.csv", user_id=1)