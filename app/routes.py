from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_ckeditor.utils import cleanify

from app import app, db
from app.models import Course, Project, Concept

bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)

course1 = Course(
    title='100 Days of Code',
    platform='Udemy',
    instructor='Angela Yu',
    has_cert=True
)

course2 = Course(
    title='CS50: Introduction to Programming with Python',
    platform='edX',
    instructor='David Malan',
    has_cert=False
)

proj1 = Project(
    project_title='tic tac toe',
    project_repo='tic-tac-toe',
    concept='flask',
    course='100 Days of Code',
    section='Day 84',
    lecture='Assignment 3'
)

proj2 = Project(
    project_title='cookie jar',
    project_repo='cookie-jar',
    concept='OOP',
    course='CS50: Introduction to Programming with Python',
    section='Week 8',
    lecture='Object Oriented Programming'
)

concept1 = Concept(
    concept_term='flask',
    category='framework',
    description='python framework for web development'
)

concept2 = Concept(
    concept_term='OOP',
    category='data structures',
    description='using python classes for object oriented programming'
)

concept3 = Concept(
    concept_term='SQLAlchemy',
    category='database',
    description='python package for db creation and maintenance'
)


@app.route('/')
def home():
    # Query db for all courses. Convert to python list
    get_courses = db.session.execute(db.select(db.select(Course)).scalars().all())

    return render_template('index.html')

# # test create items in db
# with app.app_context():
#     db.session.add_all([course1, course2, proj1, proj2, concept1, concept2, concept3])
#     db.session.commit()

