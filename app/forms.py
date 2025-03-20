from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateField, DecimalField, TextAreaField, Field, SelectField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import InputRequired, URL, Optional, ValidationError, EqualTo
from wtforms.widgets import TextInput
from app import db
from app.models import Course, Project, Concept, User

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


# USER FORMS
class RegisterForm(FlaskForm):
    email = StringField("Email",
                        validators=[
                            InputRequired()
                        ]
                        )
    name = StringField("Username",
                       validators=[
                           InputRequired()
                       ]
                       )
    display_name = StringField("Display Name",
                       validators=[
                           InputRequired()
                       ]
                       )
    password = StringField("Password",
                           validators=[
                               InputRequired()
                           ]
                           )
    password2 = StringField('Re-enter Password',
                            validators=[
                                InputRequired(),
                                EqualTo('password')
                            ])
    submit = SubmitField("Sign Up")

class EditProfileForm(FlaskForm):
    name = StringField("Username", validators=[InputRequired()])
    display_name = StringField("Display Name", validators=[InputRequired()])
    submit = SubmitField("Submit")

class PasswordReset(FlaskForm):
    codeword = StringField("Code Word", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired()])
    password = StringField("New Password", validators=[
        InputRequired(),
        EqualTo('confirm', message='Passwords must match')])
    confirm = StringField("Re-enter Password")
    submit = SubmitField("Change Password")


# Create a LoginForm to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired()])
    password = StringField("Password", validators=[InputRequired()])
    submit = SubmitField("Log In")


# CREATE FORMS

class NewCourseForm(FlaskForm):
    name = StringField("Course Name", validators=[InputRequired()])
    platform = StringField("Platform")
    url = StringField("Course URL", validators=[Optional(), URL()])
    instructor = StringField("Instructor")
    start_date = DateField("Start Date", validators=[Optional()])
    complete_date = DateField("Complete Date", validators=[Optional()])
    content_hours = DecimalField("Content Hours", validators=[Optional()])
    has_cert = BooleanField("Certificate Upon Completion?")
    submit = SubmitField("Submit")


class NewProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[InputRequired()])
    course = SelectField('Course', coerce=str)
    repo = SelectField("Project Repository", coerce=int)
    description = TextAreaField("Project Description/Parameters", validators=[Optional()])
    assignment_link = StringField("Link to Assignment", validators=[Optional(), URL()])
    start_date = DateField("Start Date", validators=[Optional()])
    complete_date = DateField("Complete Date", validators=[Optional()])
    concepts = ConceptListField('Concepts')
    section = StringField("Course Section")
    lecture = StringField("Course Lecture or Lesson")
    submit = SubmitField("Submit")


class NewCodeLinkForm(FlaskForm):
    name = StringField("CodeLink Name", validators=[InputRequired()])
    link = StringField("CodeLink URL", validators=[InputRequired(), URL()])
    project = SelectField('Project', coerce=int)
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Submit")


class NewConceptForm(FlaskForm):
    concept_term = StringField("Concept or Term", validators=[InputRequired()])
    category = RadioField("Category",
                           choices=[
                               ('library', 'Library'),
                               ('api', 'API'),
                               ('tool', 'Tool'),
                               ('resource', 'Resource'),
                               ('topic', 'Topic'),
                               ('function', 'Function'),
                               ('other', 'Other'),
                           ], coerce=str)
    description = TextAreaField("Description")
    submit = SubmitField("Submit")


class NewLibraryForm(FlaskForm):
    name = StringField("Library Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    doc_link = StringField("Docs URL", validators=[Optional(), URL()])
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Submit")


class NewAPIForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    url = StringField("API URL", validators=[Optional(), URL()])
    doc_link = StringField("Docs URL", validators=[Optional(), URL()])
    requires_login = BooleanField("Requires Login?")
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Submit")


class NewToolForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    type = RadioField("Tool/Utility Type",
                      choices=[
                          ('essentials', 'Code Essentials'),
                          ('gamedev', 'Game Development'),
                          ('code-execution', 'Code Execution'),
                          ('data-science', 'Data Science'),
                          ('documentation', 'Documentation'),
                          ('styling', 'Styling & UI'),
                          ('auth', 'Authentication'),
                          ('storage', 'Storage'),
                          ('other', 'Other'),
                      ], coerce=str)
    url = StringField("Tool URL", validators=[Optional(), URL()])
    doc_link = StringField("Docs URL", validators=[Optional(), URL()])
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Submit")


class NewResourceForm(FlaskForm):
    name = StringField("Resource Name", validators=[InputRequired()])
    description = TextAreaField("Description")
    type = RadioField("Resource Type",
                      choices=[
                            ('code', 'Code'),
                            ('cheatsheet', 'Cheatsheet'),
                            ('diagram', 'Diagram'),
                            ('quickref', 'Quick Reference'),
                            ('template', 'Template'),
                            ('other', 'Other'),
                          ], coerce=str)
    resource_url = StringField("Resource URL", validators=[Optional(), URL()])
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Submit")


# UPDATE FORMS
class UpdateProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[InputRequired()])
    description = TextAreaField("Project Description/Parameters", validators=[Optional()])
    assignment_link = StringField("Link to Assignment", validators=[Optional(), URL()])
    start_date = DateField("Start Date", validators=[Optional()])
    complete_date = DateField("Complete Date", validators=[Optional()])
    section = StringField("Course Section")
    lecture = StringField("Course Lecture or Lesson")
    concepts = ConceptListField('Concepts')
    submit = SubmitField("Submit")


# DELETE FORM
class DeleteForm(FlaskForm):
    submit = SubmitField("Confirm Delete")

# BULK IMPORT - CSV FILE FORMS
class UploadForm(FlaskForm):
    upload = FileField('csv', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'csv files only!')
    ])
    submit = SubmitField("Submit")






