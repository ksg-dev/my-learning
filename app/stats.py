# Gets SQL data from db and uses pandas/numpy to produce dashboard stats
import pandas as pd
import numpy as np
from app import app, db
from app.models import Event, Course, Project, Concept
from app.events import GetEvents, validate_id
from datetime import datetime


class Dashboard:
    def __init__(self, user):
        self.user = user
        self.refresh_events(user)

    def refresh_events(self, user):
        get_my_events = GetEvents(user)
        my_events = get_my_events.events

        for event in my_events:
            validate = validate_id(event["id"])

            if validate is None:
                new_event = Event(
                    id=event["id"],
                    type=event["type"],
                    repo=event["repo"],
                    commits=event["commits"],
                    create_type=event["create_type"],
                    timestamp=datetime.fromisoformat(event["timestamp"])
                )

                print(type(new_event.timestamp))

                db.session.add(new_event)
                db.session.commit()

    def event_stats(self):
        events_df = pd.read_sql("events", db.get_engine())

        all_commits = int(events_df["commits"].sum())
        today = events_df[events_df.timestamp == datetime.today()]
        month = events_df[events_df.timestamp.dt.month == datetime.today().month]

        today_commits = int(today["commits"].sum())
        month_commits = int(month["commits"].sum())

        return all_commits, today_commits, month_commits

    def course_stats(self):
        pass
    def project_stats(self):
        pass

    def concept_stats(self):
        pass