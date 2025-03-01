# Gets SQL data from db and uses pandas/numpy to produce dashboard stats
import pandas as pd
import numpy as np
from app import app, db
from app.models import Event, Course, Project, Concept, Repository
# from app.events import GetGitHub, validate_id
from datetime import datetime, timedelta, date
from sqlalchemy.orm import sessionmaker
from app.github import GetGitHub


class Dashboard:
    def __init__(self, user_id, user):
        self.user = user
        self.user_id = user_id
        self.github_data = GetGitHub(user)
        self.feed = self.build_feed(self.github_data.events)
        self.course_data = self.get_course_stats()
        self.event_stats = self.get_event_stats(self.github_data.events)
        self.commit_stats_chart = self.get_commit_chart_data(self.github_data.commits_data)
        # self.recent_repos = self.github_data.recent_repos
        # self.repo_stats = self.repo_activity_stats(self.github_data.repo_activity)


    # Format timedelta into string for feed
    def format_timedelta(self, td):
        seconds = int(td.total_seconds())
        if seconds < 60:
            return f"{seconds}sec"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}min"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}hr"
        else:
            days = seconds // 86400
            return f"{days}d"

    def build_feed(self, event_data):
        feed = []

        now = datetime.now()

        for item in event_data:
            timestamp = item['timestamp']
            delta = now - timestamp
            formatted_delta = self.format_timedelta(delta)
            event = {
                "delta": formatted_delta,
                "action": item["action"],
                "repo": item["repo"]
            }

            feed.append(event)

        return feed

    def get_course_stats(self):
        engine = db.get_engine()
        Session = sessionmaker(bind=engine)
        session = Session()

        # Query db
        query = session.query(Course).where(Course.user_id == self.user_id)

        pd.set_option("expand_frame_repr", False)
        # df = pd.read_sql(query.statement, engine)
        # print(f"df: {df}")

        courses_df = pd.read_sql(query.statement, engine)
        courses_df.start = pd.to_datetime(courses_df.start)
        courses_df.complete = pd.to_datetime(courses_df.complete)
        # print(courses_df)
        # print(courses_df.info())
        # print("---------------------------")

        # Content Stats for ALL
        all_courses_hr = courses_df["content_hours"].sum()

        # NOT STARTED Stats
        not_started = courses_df[courses_df["status"] == "not-started"]
        not_started_count = not_started["name"].count()
        not_started_hours = not_started["content_hours"].sum()

        # IN PROGRESS Stats
        in_progress = courses_df[courses_df["status"] == "in-progress"]
        in_progress_count = in_progress["name"].count()
        in_progress_hours = in_progress["content_hours"].sum()

        # COMPLETE Stats
        complete = courses_df[courses_df["status"] == "complete"]
        complete_count = complete["name"].count()
        complete_hours = complete["content_hours"].sum()

        start_min = complete["start"].min()
        start_max = complete["start"].max()
        complete_min = complete["complete"].min()
        complete_max = complete["complete"].max()

        # Add column for days it took to complete
        complete["days_to_complete"] = complete["complete"] - complete["start"]

        # PER COURSE Average content hr complete per day (content hr / days)
        complete["avg_daily_content"] = complete["days_to_complete"] / complete["content_hours"]
        # print(content)

        # Overall Average content covered daily
        avg_daily = complete['avg_daily_content'].mean()

        # print(complete)
        # print(complete.info())

        course_progress = [
            {
                "all-courses": {
                    "hours": all_courses_hr,
                    "start-min": start_min,
                    "start-max": start_max,
                    "avg-daily-content": avg_daily,
                },
                "not-started": {
                    "count": not_started_count,
                    "hours": not_started_hours,
                },
                "in-progress": {
                    "count": in_progress_count,
                    "hours": in_progress_hours,
                },
                "complete": {
                    "count": complete_count,
                    "hours": complete_hours,
                }
            }
        ]


        course_stats = {
            "all-course-hr": all_courses_hr,
            "not-started-count": not_started_count,
            "not_started_hours": not_started_hours,
            "in-progress-count": in_progress_count,
            "in_progress_hours": in_progress_hours,
            "complete-count": complete_count,
            "complete-hours": complete_hours,
            "start-min": start_min,
            "start-max": start_max,
            "complete-min": complete_min,
            "complete-max": complete_max,
            "avg-daily-content": avg_daily
        }

        # print(course_stats)
        return course_stats

    def get_event_stats(self, events):
        # events = self.github_data.events

        all_commits = 0
        last_mo_commits = 0
        mo_commits = 0
        last_wk_commits = 0
        wk_commits = 0

        today = date.today()

        iso = today.isocalendar()
        last_wk = iso.week - 1
        last_mo = today.month - 1
        # for i in iso:
        #     print(i)


        for event in events:
            action = event["action"].split()
            iso_stamp = event["timestamp"].isocalendar()
            # for i in iso_stamp:
            #     print(i)

        #     # date_diff = today - event["timestamp"]
        #
        #     print(f"action: {action}")
            # print(f"datediff: {date_diff}")
            # print(date.fromtimestamp(event["timestamp"]))

            if "Pushed" in action[0]:
                all_commits += int(action[1])
                # print("-------------------")
                # print(f"action: {action}")
                # print(f"iso_stamp: {iso_stamp}")
                # print(f"date stamp: {event['timestamp']}")

                # Check weekly
                # If iso timestamp for week == this week
                if iso_stamp[1] == iso[1]:
                    wk_commits += int(action[1])
                    # print("This week")

                # else if iso timestamp week == last week
                elif iso_stamp[1] == last_wk:
                    last_wk_commits += int(action[1])
                    # print("Last week")

                # Check Monthly
                # If timestamp month == this month
                if event["timestamp"].month == today.month:
                    mo_commits += int(action[1])
                    # print("This month")

                # else if timestamp month == last month
                elif event["timestamp"].month == last_mo:
                    last_mo_commits += int(action[1])
                    # print("Last Month")

        month_diff = mo_commits - last_mo_commits
        wk_diff = wk_commits - last_wk_commits

        if mo_commits != 0:
            mon_percent = (month_diff / mo_commits) * 100
        else:
            mon_percent = 100

        if last_wk_commits != 0:
            wk_percent = (wk_diff / last_wk_commits) * 100
        else:
            wk_percent = 100

        stats = {
            "all-commits": all_commits,
            "this-week": wk_commits,
            "last-week": last_wk_commits,
            "this-month": mo_commits,
            "last-month": last_mo_commits,
            "mo-change": mon_percent,
            "wk-change": wk_percent
        }
        # print("------TOTALS-------")
        # print(f"This week: {wk_commits}")
        # print(f"Last week: {last_wk_commits}")
        # print(f"This Month: {mo_commits}")
        # print(f"Last Month: {last_mo_commits}")
        # print(f"Total Commits: {all_commits}")
        return stats

    # Take commit data and convert to pd df to get commit count on all branches
    def get_commit_chart_data(self, commit_data):
        df = pd.DataFrame(commit_data)
        df["timestamps"] = pd.to_datetime(df["timestamps"])
        # Add column for months
        df["month"] = df.timestamps.dt.month
        # Get value counts for each month - returns series w month number as index
        monthly = df.month.value_counts()
        # Get today, and last 6 mo, convert to month number only for xaxis
        today = date.today().month
        month_ends = pd.date_range(end=date.today(), freq="ME", periods=6)
        month_index = month_ends.month
        # Reindex monthly value counts w last 6 months
        by_month = monthly.reindex(month_index).fillna(0)
        # print(by_month)

        return by_month





    # def get_event_stats(self):
    #     engine = db.get_engine()
    #     Session = sessionmaker(bind=engine)
    #     session = Session()
    #
    #     # Query db
    #     query = session.query(Event).join(Repository)
    #
    #     pd.set_option("expand_frame_repr", False)
    #     # df = pd.read_sql(query.statement, engine)
    #     # print(f"df: {df}")
    #
    #     try:
    #         # events_df = pd.read_sql("events", db.get_engine())
    #         events_df = pd.read_sql(query.statement, engine)
    #         # print(events_df)
    #         # print("---------------------------")
    #
    #         # Stats for ALL
    #         all_commits = int(events_df["commits"].sum())
    #         all_commits_by_repo = events_df.groupby("repo_id")["commits"].sum()
    #         # print(f"all_by_repo: {all_commits_by_repo}")
    #
    #         # Stats for TODAY
    #         today = events_df[events_df.timestamp == datetime.today()]
    #         # print(f"today_df: {today}")
    #         yesterday = events_df[events_df.timestamp == (datetime.today() - timedelta(days=1))]
    #         # print(f"yest_df: {yesterday}")
    #         yest_count = int(yesterday["commits"].sum())
    #         today_count = int(today["commits"].sum())
    #         today_by_repo = today.groupby("repo_id")["commits"].sum()
    #
    #         if yest_count != 0:
    #             day_change = (today_count - yest_count) / yest_count * 100
    #         else:
    #             day_change = 0
    #
    #         # Stats for MONTH
    #         month = events_df[events_df.timestamp.dt.month == datetime.today().month]
    #         last_mo = events_df[events_df.timestamp.dt.month == datetime.today().month - 1]
    #         ltmo_count = int(last_mo["commits"].sum())
    #         month_count = int(month["commits"].sum())
    #         month_by_repo = month.groupby("repo_id")["commits"].sum()
    #
    #         if ltmo_count != 0:
    #             mo_change = (month_count - ltmo_count) / ltmo_count * 100
    #         else:
    #             mo_change = 0
    #
    #         # Stats for YEAR
    #         year = events_df[events_df.timestamp.dt.year == datetime.today().year]
    #         last_yr = events_df[events_df.timestamp.dt.year == datetime.today().year - 1]
    #         ltyr_count = int(last_yr["commits"].sum())
    #         year_count = int(year["commits"].sum())
    #         year_by_repo = year.groupby("repo_id")["commits"].sum()
    #
    #         if ltyr_count != 0:
    #             yr_change = (year_count - ltyr_count) / ltyr_count * 100
    #         else:
    #             yr_change = 0
    #
    #         event_stats = {
    #             "all_commits": all_commits,
    #             "all_by_repo": all_commits_by_repo,
    #             "yest_commits": yest_count,
    #             "today_commits": today_count,
    #             "day_change": day_change,
    #             "today_by_repo": today_by_repo,
    #             "ltmo_commits": ltmo_count,
    #             "month_commits": month_count,
    #             "mo_change": mo_change,
    #             "month_by_repo": month_by_repo,
    #             "ltyr_commits": ltyr_count,
    #             "year_commits": year_count,
    #             "yr_change": yr_change,
    #             "year_by_repo": year_by_repo
    #         }
    #     except KeyError:
    #         event_stats = {
    #             "all_commits": 0,
    #             "all_by_repo": 0,
    #             "yest_commits": 0,
    #             "today_commits": 0,
    #             "day_change": 0,
    #             "today_by_repo": 0,
    #             "ltmo_commits": 0,
    #             "month_commits": 0,
    #             "mo_change": 0,
    #             "month_by_repo": 0,
    #             "ltyr_commits": 0,
    #             "year_commits": 0,
    #             "yr_change": 0,
    #             "year_by_repo": 0
    #         }
    #     # print(f"event_stats: {event_stats}")
    #     return event_stats
    #
    # def get_stats_by_time(self):
    #
    #     pass






