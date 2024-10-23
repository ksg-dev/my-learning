# Gets SQL data from db and uses pandas/numpy to produce dashboard stats
import pandas as pd
import numpy as np
from app import app, db
from app.models import Event, Course, Project, Concept, Repository
from app.events import GetGitHub, validate_id
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker


class Dashboard:
    def __init__(self, user_id, user):
        self.user = user
        self.user_id = user_id
        self.refresh_events(user)

    def refresh_events(self, user):
        # Get Github API Events/Repos Data
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
                    repo_id=event["repo_id"],
                    commits=event["commits"],
                    create_type=event["create_type"],
                    timestamp=datetime.fromisoformat(event["timestamp"]),
                    user_id=self.user_id
                )

                db.session.add(new_event)

                # target_repo = db.session.execute(db.select(Repository).where(Repository.id == event["repo_id"])).scalar()
                # target_repo.events.append(new_event)

                # if not validate_repo:
                #     new_repo = Repository(
                #         id=event["repo_id"],
                #         name=event["repo"],
                #         user_id=self.user_id
                #     )
                #
                #     db.session.add(new_repo)

                db.session.commit()

    def get_event_stats(self):
        engine = db.get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Query db
        query = session.query(Event).join(Repository)

        pd.set_option("expand_frame_repr", False)
        # df = pd.read_sql(query.statement, engine)
        # print(f"df: {df}")

        try:
            # events_df = pd.read_sql("events", db.get_engine())
            events_df = pd.read_sql(query.statement, engine)
            # print(events_df)
            # print("---------------------------")

            # Stats for ALL
            all_commits = int(events_df["commits"].sum())
            all_commits_by_repo = events_df.groupby("repo_id")["commits"].sum()
            # print(f"all_by_repo: {all_commits_by_repo}")

            # Stats for TODAY
            today = events_df[events_df.timestamp == datetime.today()]
            # print(f"today_df: {today}")
            yesterday = events_df[events_df.timestamp == (datetime.today() - timedelta(days=1))]
            # print(f"yest_df: {yesterday}")
            yest_count = int(yesterday["commits"].sum())
            today_count = int(today["commits"].sum())
            today_by_repo = today.groupby("repo_id")["commits"].sum()

            if yest_count != 0:
                day_change = (today_count - yest_count) / yest_count * 100
            else:
                day_change = 0

            # Stats for MONTH
            month = events_df[events_df.timestamp.dt.month == datetime.today().month]
            last_mo = events_df[events_df.timestamp.dt.month == datetime.today().month - 1]
            ltmo_count = int(last_mo["commits"].sum())
            month_count = int(month["commits"].sum())
            month_by_repo = month.groupby("repo_id")["commits"].sum()

            if ltmo_count != 0:
                mo_change = (month_count - ltmo_count) / ltmo_count * 100
            else:
                mo_change = 0

            # Stats for YEAR
            year = events_df[events_df.timestamp.dt.year == datetime.today().year]
            last_yr = events_df[events_df.timestamp.dt.year == datetime.today().year - 1]
            ltyr_count = int(last_yr["commits"].sum())
            year_count = int(year["commits"].sum())
            year_by_repo = year.groupby("repo_id")["commits"].sum()

            if ltyr_count != 0:
                yr_change = (year_count - ltyr_count) / ltyr_count * 100
            else:
                yr_change = 0

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
        except KeyError:
            event_stats = {
                "all_commits": 0,
                "all_by_repo": 0,
                "yest_commits": 0,
                "today_commits": 0,
                "day_change": 0,
                "today_by_repo": 0,
                "ltmo_commits": 0,
                "month_commits": 0,
                "mo_change": 0,
                "month_by_repo": 0,
                "ltyr_commits": 0,
                "year_commits": 0,
                "yr_change": 0,
                "year_by_repo": 0
            }
        # print(f"event_stats: {event_stats}")
        return event_stats

    def get_course_stats(self):
        engine = db.get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Query db
        query = session.query(Course)

        pd.set_option("expand_frame_repr", False)
        # df = pd.read_sql(query.statement, engine)
        # print(f"df: {df}")

        courses_df = pd.read_sql(query.statement, engine)
        print(courses_df)
        print("---------------------------")

        # Content Stats for ALL
        all_courses_hr = courses_df["content_hours"].sum()

        # NOT STARTED Stats
        not_started = courses_df[courses_df["status"] == "not-started"]
        not_started_count = not_started["name"].count()

        # IN PROGRESS Stats
        in_progress = courses_df[courses_df["status"] == "in-progress"]
        in_progress_count = in_progress["name"].count()

        # COMPLETE Stats
        complete = courses_df[courses_df["status"] == "complete"]
        complete_count = complete["name"].count()

        start_min = complete["start"].min()
        start_max = complete["start"].max()
        complete_min = complete["complete"].min()
        complete_max = complete["complete"].max()

        course_stats = {
            "all-course-hr": all_courses_hr,
            "not-started-count": not_started_count,
            "in-progress-count": in_progress_count,
            "complete-count": complete_count,
            "start-min": start_min,
            "start-max": start_max,
            "complete-min": complete_min,
            "complete-max": complete_max
           }
        print(course_stats)
        return course_stats


    def get_project_stats(self):
        pass

    def get_concept_stats(self):
        pass