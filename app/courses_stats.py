# Gets SQL Data from db-Courses, uses numpy/pandas to produce course stats
import pandas as pd
import numpy as np
from app import db
from app.models import Course, Project, Event, Repository
import plotly.express as px


class CourseStats:
    def __init__(self):
        self.course_df = pd.read_sql("courses", db.get_engine())
        self.project_df = pd.read_sql("projects", db.get_engine())
        self.event_df = pd.read_sql("events", db.get_engine())
        self.repo_df = pd.read_sql("repos", db.get_engine())

    def course_timeline(self):
        courses = self.course_df
        projects = self.project_df
        events = self.event_df
        repos = self.repo_df

        by_platform = courses.groupby(by="platform").count()
        # fig = px.timeline(df, x_start=df.start, x_end=df.complete, y=df.platform, color=df.title)

        repo_events =

        # projects_by_course = projects.groupby(by="course_id").count()

        return repos.info()





stats = CourseStats()
print(stats.course_timeline())