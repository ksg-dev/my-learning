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
from app.models import Course, Project, Concept, Library, Tool, Resource
from app.forms import NewCourseForm, NewProjectForm, NewConceptForm

bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)


@app.route('/')
@app.route('/index')
def home():
    # Query db for all courses. Convert to python list
    get_courses = db.session.execute(db.select(Course)).scalars().all()
    courses = [course for course in get_courses]

    # Query db for all projects. Convert to python list
    get_projects = db.session.execute(db.select(Project)).scalars().all()
    projects = [project for project in get_projects]

    # # Query db for all concepts. Convert to python list
    # get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    # concepts = [concept for concept in get_concepts]

    return render_template('index.html', all_courses=courses, all_projects=projects)


@app.route('/concepts')
def concepts_page():
    # Get concepts
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    concepts = [concept for concept in get_concepts]

    return render_template('concepts.html', concepts=concepts)


@app.route('/courses')
def courses_page():
    # Get courses
    get_courses = db.session.execute(db.select(Course)).scalars().all()
    courses = [course for course in get_courses]

    return render_template('courses.html', courses=courses)


@app.route('/projects')
def projects_page():
    # Get projects
    get_projects = db.session.execute(db.select(Project)).scalars().all()
    projects = [project for project in get_projects]

    return render_template('projects.html', projects=projects)


@app.route('/libraries')
def libraries_page():
    # Get libraries
    get_libraries = db.session.execute(db.select(Library)).scalars().all()
    libraries = [library for library in get_libraries]

    return render_template('libraries.html', libraries=libraries)


@app.route('/tools')
def tools_page():
    # Get tools
    get_tools = db.session.execute(db.select(Tool)).scalars().all()
    tools = [tool for tool in get_tools]

    return render_template('tools.html', tools=tools)


@app.route('/resources')
def resources_page():
    # Get resources
    get_resources = db.session.execute(db.select(Resource)).scalars().all()
    resources = [resource for resource in get_resources]

    return render_template('resources.html', resources=resources)


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
    return render_template('add.html', form=form, object="Course")


@app.route('/add-project/<int:course_id>', methods=["GET", "POST"])
def add_new_project(course_id):
    target_course = db.session.execute(db.select(Course).where(Course.id == course_id)).scalar()
    form = NewProjectForm()
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]


    if form.validate_on_submit():
        new_proj = Project(
            project_title=form.project_title.data,
            project_repo=form.repo.data,
            course=target_course,
            section=form.section.data,
            lecture=form.lecture.data,
            date_added=date.today()
        )

        db.session.add(new_proj)

        if form.concepts.data:
            for concept_name in form.concepts.data:
                concept = Concept.query.filter_by(concept_term=concept_name.lower()).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name
                    )

                    db.session.add(concept)

                new_proj.concepts.append(concept)


        print(f"title: {new_proj.project_title}")
        print(f"repo: {new_proj.project_repo}")
        print(f"concepts: {new_proj.concepts}")
        print(f"course: {new_proj.course}")
        print(f"section: {new_proj.section}")
        print(f"lecture: {new_proj.lecture}")



        # print(new_proj)

        db.session.add(new_proj)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('add.html', form=form, object="Project")


@app.route('/courses/<int:num>')
def course_detail(num):
    target_course = db.get_or_404(Course, num)
    all_projects = db.session.execute(db.select(Project).filter_by(course_id=num)).scalars().all()

    course_concepts = {}

    # Add all concepts to dict as key, and count of occurrence as value
    for proj in all_projects:
        for concept in proj.concepts:
            if concept.concept_term in course_concepts:
                course_concepts[concept.concept_term] += 1
            else:
                course_concepts[concept.concept_term] = 1

    # Sort descending
    sorted_concepts = dict(
        sorted(course_concepts.items(), key=lambda item: item[1], reverse=True))

    return render_template('course-detail.html', course=target_course, all_projects=all_projects, top_concepts=sorted_concepts)