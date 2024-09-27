from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField, DecimalField
from wtforms.validators import InputRequired
from app import db
from app.models import Course, Project, Concept


class NewCourseForm(FlaskForm):
    title = StringField("Course Title", validators=[InputRequired()])
    platform = StringField("Platform")
    instructor = StringField("Instructor")
    start_date = DateField("Start Date")
    content_hours = DecimalField("Content Hours")
    has_cert = BooleanField("Certificate Upon Completion?", validators=[InputRequired()])
    submit = SubmitField("Add Course")


class NewProjectForm(FlaskForm):
    project_title = StringField("Project Title", validators=[InputRequired()])
    repo = StringField("Project Repository", validators=[InputRequired()])
    concept = StringField("Concepts", validators=[InputRequired()])
    course = StringField("Course")
    section = StringField("Course Section")
    lecture = StringField("Course Lecture or Lesson")

