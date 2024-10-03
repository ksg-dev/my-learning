from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField, DecimalField, TextAreaField, Field, SelectField
from wtforms.validators import InputRequired, URL
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
    complete_date = DateField("Complete Date")
    content_hours = DecimalField("Content Hours")
    has_cert = BooleanField("Certificate Upon Completion?")
    submit = SubmitField("Add Course")


class NewProjectForm(FlaskForm):
    project_title = StringField("Project Title", validators=[InputRequired()])
    repo = StringField("Project Repository", validators=[InputRequired()])
    start_date = DateField("Start Date")
    complete_date = DateField("Complete Date")
    concepts = ConceptListField('Concepts')
    section = StringField("Course Section")
    lecture = StringField("Course Lecture or Lesson")
    submit = SubmitField("Add Project")


class NewConceptForm(FlaskForm):
    concept = StringField("Concept or Term", validators=[InputRequired()])
    category = StringField("Category")
    description = TextAreaField("Description")
    submit = SubmitField("Add Concept")


class NewLibraryForm(FlaskForm):
    name = StringField("Library Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    doc_link = StringField("Docs URL", validators=[URL()])
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Add Library")


class NewAPIForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    url = StringField("API URL", validators=[URL()])
    doc_link = StringField("Docs URL", validators=[URL()])
    requires_login = BooleanField("Requires Login?")
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Add Tool")


class NewToolForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    url = StringField("Tool URL", validators=[URL()])
    doc_link = StringField("Docs URL", validators=[URL()])
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Add Tool")


class NewResourceForm(FlaskForm):
    name = StringField("Resource Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    type = SelectField("Resource Type",
                       choices=[
                           ('cheatsheet', 'Cheatsheet'),
                           ('diagram', 'Diagram'),
                           ('quickref', 'Quick Reference'),
                           ('template', 'Template'),
                           ('other', 'Other')
                       ])
    resource_url = StringField("Resource URL", validators=[URL()])
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Add Resource")


# UPDATE FORMS

class UpdateCourseForm(FlaskForm):
    pass


class UpdateProjectForm(FlaskForm):
    pass


class UpdateConceptForm(FlaskForm):
    pass



