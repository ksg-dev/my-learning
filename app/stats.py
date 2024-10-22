# Gets SQL data from db and uses pandas/numpy to produce dashboard stats
import pandas as pd
import numpy as np
from app import app, db
from app.models import Event, Course, Project, Concept, Repository
from app.events import GetGitHub, validate_id
from datetime import datetime, timedelta


class Dashboard:
    def __init__(self, user_id, user):
        self.user = user
        self.user_id = user_id
        self.refresh_events(user)

    def refresh_events(self, user):
        get_my_data = GetGitHub(user)
        my_events = get_my_data.events
        my_repos = get_my_data.repos

        for repo in my_repos:
            validate_repo1 = validate_id(Repository, repo["id"])

            if validate_repo1 is None:
                new_repo = Repository(
                    id=repo["id"],
                    name=repo["name"],
                    user_id=self.user_id
                )

                db.session.add(new_repo)
                db.session.commit()

        for event in my_events:
            validate_event = validate_id(Event, event["id"])
            validate_repo = validate_id(Repository, event["repo_id"])

            if validate_event is None:
                new_event = Event(
                    id=event["id"],
                    type=event["type"],
                    commits=event["commits"],
                    create_type=event["create_type"],
                    timestamp=datetime.fromisoformat(event["timestamp"]),
                    user_id=self.user_id
                )

                db.session.add(new_event)

                if not validate_repo:
                    new_repo = Repository(
                        id=event["repo_id"],
                        name=event["repo"],
                        user_id=self.user_id
                    )

                    db.session.add(new_repo)

                new_event.repo_id = event["repo_id"]

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
        last_mo = events_df[events_df.timestamp.dt.month == datetime.today().month - 1]
        ltmo_count = int(last_mo["commits"].sum())
        month_count = int(month["commits"].sum())
        month_by_repo = month.groupby("repo")

        if ltmo_count != 0:
            mo_change = (month_count - ltmo_count) / ltmo_count * 100
        else:
            mo_change = None

        # Stats for YEAR
        year = events_df[events_df.timestamp.dt.year == datetime.today().year]
        last_yr = events_df[events_df.timestamp.dt.year == datetime.today().year - 1]
        ltyr_count = int(last_yr["commits"].sum())
        year_count = int(year["commits"].sum())
        year_by_repo = year.groupby("repo")

        if ltyr_count != 0:
            yr_change = (year_count - ltyr_count) / ltyr_count * 100
        else:
            yr_change = None

        event_stats = {
            "all_commits": all_commits,
            "all_by_repo": all_commits_by_repo,
            "yest_commits": yest_count,
            "today_commits": today_count,
            "day_change": day_change,
            "today_by_repo": today_by_repo,
            "ltmo_commits": ltmo_count,
            "month_commits": month_count,
            "mo_change": mo_change,
            "month_by_repo": month_by_repo,
            "ltyr_commits": ltyr_count,
            "year_commits": year_count,
            "yr_change": yr_change,
            "year_by_repo": year_by_repo
        }

        return event_stats

    def get_course_stats(self):
        pass
    def get_project_stats(self):
        pass

    def get_concept_stats(self):
        pass