from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField, DecimalField, TextAreaField, Field
from wtforms.validators import InputRequired
from wtforms.widgets import TextInput
from app import db
from app.models import Course, Project, Concept


# Create Custom "Tag" Field for Concepts
class ConceptListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return ', '.join(self.data)
        else:
            return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []



# CREATE FORMS

class NewCourseForm(FlaskForm):
    title = StringField("Course Title", validators=[InputRequired()])
    platform = StringField("Platform")
    instructor = StringField("Instructor")
    start_date = DateField("Start Date")
    content_hours = DecimalField("Content Hours")
    has_cert = BooleanField("Certificate Upon Completion?")
    submit = SubmitField("Add Course")


class NewProjectForm(FlaskForm):
    project_title = StringField("Project Title", validators=[InputRequired()])
    repo = StringField("Project Repository", validators=[InputRequired()])
    concepts = ConceptListField('Concepts')
    section = StringField("Course Section")
    lecture = StringField("Course Lecture or Lesson")
    submit = SubmitField("Add Project")


class NewConceptForm(FlaskForm):
    concept = StringField("Concept or Term", validators=[InputRequired()])
    category = StringField("Category")
    description = TextAreaField("Description")
    submit = SubmitField("Add Concept")





# UPDATE FORMS

class UpdateCourseForm(FlaskForm):
    pass


class UpdateProjectForm(FlaskForm):
    pass


class UpdateConceptForm(FlaskForm):
    pass



