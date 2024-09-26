from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from datetime import date
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
from app.forms import NewCourseForm

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
    get_courses = db.session.execute(db.select(Course)).scalars().all()
    courses = [course for course in get_courses]

    # Query db for all projects. Convert to python list
    get_projects = db.session.execute(db.select(Project)).scalars().all()
    projects = [project for project in get_projects]

    # Query db for all concepts. Convert to python list
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    concepts = [concept for concept in get_concepts]

    return render_template('index.html', all_courses=courses, all_projects=projects)

# # test create items in db
# with app.app_context():
#     db.session.add_all([course1, course2, proj1, proj2, concept1, concept2, concept3])
#     db.session.commit()

@app.route('/add-course', methods=["GET", "POST"])
def add_new_course():
    form = NewCourseForm()
    if form.validate_on_submit():
        new_course = Course(
            title=form.title.data,
            platform=form.platform.data,
            instructor=form.instructor.data,
            start=form.start_date.data,
            content_hours=form.content_hours.data,
            has_cert=form.has_cert.data,
            date_added=date.today()
        )

        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('add-course.html', form=form)


