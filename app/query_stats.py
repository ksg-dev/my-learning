# Gets SQL Data from db-Courses, uses numpy/pandas to produce course stats
import pandas as pd
import numpy as np
from app import db
from app.models import Course, Project, Event, Repository
import plotly.express as px
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select



# engine = db.get_engine()

# Session = sessionmaker(bind=engine)
# session = Session()

# result = db.session.execute(select(Event).order_by(Event.timestamp))
# print(result.all())

# course_data = select(Event, Repository).join(Event.repo).order_by(Event.timestamp))
# for row in db.session.execute(course_data):
#     print(f"Event: {row.Event.type} - {row.Repository.name}")

# Query db
# query = session.query(Course).join(Project)

# pd.set_option("expand_frame_repr", False)

# Convert query result to df
# df = pd.read_sql(query.statement, engine)

# print(df)

# class CourseStats:
#     def __init__(self):
#         self.course_df = pd.read_sql("courses", db.get_engine())
#         self.project_df = pd.read_sql("projects", db.get_engine())
#         self.event_df = pd.read_sql("events", db.get_engine())
#         self.repo_df = pd.read_sql("repos", db.get_engine())
#
#     def course_timeline(self):
#         courses = self.course_df
#         projects = self.project_df
#         events = self.event_df
#         repos = self.repo_df
#
#         by_platform = courses.groupby(by="platform").count()
#         # fig = px.timeline(df, x_start=df.start, x_end=df.complete, y=df.platform, color=df.title)
#
#         repo_events =
#
#         # projects_by_course = projects.groupby(by="course_id").count()
#
#         return repos.info()
#
#
#
#
#
# stats = CourseStats()
# print(stats.course_timeline())