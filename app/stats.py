# Gets SQL data from db and uses pandas/numpy to produce dashboard stats
import pandas as pd
import numpy as np
from app import app, db
from app.models import Event, Course, Project, Concept
from app.events import GetEvents, validate_id
from datetime import datetime, timedelta


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

                # print(type(new_event.timestamp))

                db.session.add(new_event)
                db.session.commit()

    def get_event_stats(self):
        events_df = pd.read_sql("events", db.get_engine())

        # Stats for ALL
        all_commits = int(events_df["commits"].sum())
        all_commits_by_repo = events_df.groupby("repo")

        # Stats for TODAY
        today = events_df[events_df.timestamp == datetime.today()]
        yesterday = events_df[events_df.timestamp == (datetime.today() - timedelta(days=1))]
        yest_count = int(yesterday["commits"].sum())
        today_count = int(today["commits"].sum())
        today_by_repo = today.groupby("repo")

        if yest_count != 0:
            day_change = (today_count - yest_count) / yest_count * 100
        else:
            day_change = None

        # Stats for MONTH
        month = events_df[events_df.timestamp.dt.month == datetime.today().month]
        month_count = int(month["commits"].sum())
        month_by_repo = month.groupby("repo")

        # Stats for YEAR
        year = events_df[events_df.timestamp.dt.year == datetime.today().year]
        year_count = int(year["commits"].sum())
        year_by_repo = year.groupby("repo")

        event_stats = {
            "all_commits": all_commits,
            "all_by_repo": all_commits_by_repo,
            "yest_commits": yest_count,
            "today_commits": today_count,
            "day_change": day_change,
            "today_by_repo": today_by_repo,
            "month_commits": month_count,
            "month_by_repo": month_by_repo,
            "year_commits": year_count,
            "year_by_repo": year_by_repo
        }

        return event_stats

    def get_course_stats(self):
        pass
    def get_project_stats(self):
        pass

    def get_concept_stats(self):
        pass