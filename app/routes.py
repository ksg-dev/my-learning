import datetime

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap5
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_ckeditor.utils import cleanify
from dotenv import load_dotenv
import os
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, current_user, logout_user, login_required


from app import app, db
from app.models import User, Course, Project, Concept, Library, API, Tool, Resource, Event, Repository
from app.forms import RegisterForm, LoginForm,NewCourseForm, NewProjectForm, NewConceptForm, NewAPIForm, NewLibraryForm, NewToolForm, NewResourceForm
from app.events import GetEvents, validate_id
from app.stats import Dashboard

bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)

load_dotenv()

DB_URI = os.environ["DB_URI"]

GH_USERNAME = os.environ["GITHUB_USERNAME"]

# To show resource categories across pages
resource_categories = {
    'cheatsheet': ['Cheatsheet', 'bg-warning text-dark', 'bi-file-earmark-text'],
    'diagram': ['Diagram', 'bg-primary', 'bi-diagram-2'],
    'quickref': ['Quick Reference', 'bg-info text-dark', 'bi-info-circle'],
    'template': ['Template', 'bg-success', 'bi-file-ruled'],
    'other': ['Other', 'bg-secondary', 'bi-collection']
}

# To show concept categories across pages
concept_categories = {
    'library': ['Cheatsheet', 'bg-warning text-dark', 'bi-file-earmark-text'],
    'api': ['Diagram', 'bg-primary', 'bi-diagram-2'],
    'tool': ['Quick Reference', 'bg-info text-dark', 'bi-info-circle'],
    'resource': ['Template', 'bg-success', 'bi-file-ruled'],
    'other': ['Other', 'bg-secondary', 'bi-collection']
}


##################################### LOGIN/REGISTER PAGES ########################################


# Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        entered_email = form.email.data
        user_check = db.session.execute(db.select(User).where(User.email == entered_email)).scalar()
        if user_check:
            flash("That email is already registered. Login instead")
            return redirect(url_for("login", form=form))
        else:
            new_user = User(
                email=entered_email,
                name=form.name.data.title(),
                display_name=form.display_name.data,
                password= generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
            )

            db.session.add(new_user)
            db.session.commit()

            # Login and authenticate user after adding details to db
            login_user(new_user)

            return redirect(url_for("home"))

    return render_template("register.html", form=form)


# Retrieve a user from the database based on their email.
@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        login_password = form.password.data

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, login_password):
                login_user(user)

                return redirect(url_for("home"))

            else:
                flash("Email/Password combination incorrect")
                return redirect(url_for("login", form=form))

        else:
            flash("We have no record of that email. Please try again.")
            return redirect(url_for("login", form=form))

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/')
@app.route('/index')
@login_required
def home():
    # Create Dashboard Object - refresh events
    dashboard = Dashboard(user=current_user.name, user_id=current_user.id)
    now = datetime.utcnow()

    # Query db for repo activity, convert to python list
    get_repos = db.session.execute(db.select(Repository).filter_by(user_id=current_user.id)).scalars().all()
    repos = [repo for repo in get_repos]

    # Get event stats dict
    my_events = dashboard.get_event_stats()

    # Query db for all courses. Convert to python list
    get_courses = db.session.execute(db.select(Course)).scalars().all()
    courses = [course for course in get_courses]

    # Query db for all projects. Convert to python list
    get_projects = db.session.execute(db.select(Project)).scalars().all()
    projects = [project for project in get_projects]

    # # Query db for all concepts. Convert to python list
    # get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    # concepts = [concept for concept in get_concepts]

    recent = db.session.execute(db.select(Event).order_by(Event.timestamp.desc())).scalars().yield_per(10)
    recent_events = [event for event in recent]


    # for i in recent_events:
    #     if now.day == i.timestamp.day:
    #         diff = str((now - i.timestamp).seconds // 60) + "min"
    #     else:
    #         diff = str((now - i.timestamp).days) + "days"
    #     i.append(diff)
    #
    # print(now)
    # for i in recent_events:
    #     print(i)

    return render_template('index.html', my_events=my_events, now=now, activity=recent_events, my_repos=repos)

##################################### LANDING PAGES ########################################
@app.route('/concepts')
@login_required
def concepts_page():
    # Get concepts
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    concepts = [concept for concept in get_concepts]

    return render_template('concepts.html', concepts=concepts)


@app.route('/courses')
@login_required
def courses_page():
    # Get courses
    get_courses = db.session.execute(db.select(Course).filter_by(user_id=current_user.id)).scalars().all()
    courses = [course for course in get_courses]

    return render_template('courses.html', courses=courses)


@app.route('/projects')
@login_required
def projects_page():
    # Get projects
    get_projects = db.session.execute(db.select(Project).filter_by(user_id=current_user.id)).scalars().all()
    projects = [project for project in get_projects]

    top_concepts = {}

    # Add all concepts to dict as key, and count of occurrence as value
    for proj in get_projects:
        for concept in proj.concepts:
            if concept.concept_term in top_concepts:
                top_concepts[concept.concept_term] += 1
            else:
                top_concepts[concept.concept_term] = 1

    # Sort descending
    sorted_concepts = dict(
        sorted(top_concepts.items(), key=lambda item: item[1], reverse=True))

    return render_template('projects.html', projects=projects, top_concepts=top_concepts)


@app.route('/libraries')
@login_required
def libraries_page():
    # Get libraries
    get_libraries = db.session.execute(db.select(Library).filter_by(user_id=current_user.id)).scalars().all()
    libraries = [library for library in get_libraries]

    return render_template('libraries.html', libraries=libraries)


@app.route('/apis')
@login_required
def apis_page():
    # Get apis
    get_apis = db.session.execute(db.select(API).filter_by(user_id=current_user.id)).scalars().all()
    apis = [api for api in get_apis]

    return render_template('apis.html', apis=apis)


@app.route('/tools')
@login_required
def tools_page():
    # Get tools
    get_tools = db.session.execute(db.select(Tool).filter_by(user_id=current_user.id)).scalars().all()
    tools = [tool for tool in get_tools]

    return render_template('tools.html', tools=tools)


@app.route('/resources')
@login_required
def resources_page():
    # Get resources
    get_resources = db.session.execute(db.select(Resource).filter_by(user_id=current_user.id)).scalars().all()
    resources = [resource for resource in get_resources]

    return render_template('resources.html', resources=resources, badge=resource_categories)


##################################### CREATE PAGES ########################################


@app.route('/add-course', methods=["GET", "POST"])
@login_required
def add_new_course():
    form = NewCourseForm()
    if form.validate_on_submit():
        new_course = Course(
            title=form.title.data,
            platform=form.platform.data,
            url=form.url.data,
            instructor=form.instructor.data,
            start=form.start_date.data,
            complete=form.complete_date.data,
            content_hours=form.content_hours.data,
            has_cert=form.has_cert.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for("courses_page"))
    return render_template('add.html', form=form, object="Course")


@app.route('/add-project/<int:course_id>', methods=["GET", "POST"])
@login_required
def add_new_project(course_id):
    target_course = db.session.execute(db.select(Course).where(Course.id == course_id)).scalar()
    form = NewProjectForm()
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        new_proj = Project(
            project_title=form.project_title.data,
            project_repo=form.repo.data,
            description=form.description.data,
            assignment_link=form.assignment_link.data,
            course=target_course,
            start=form.start_date.data,
            complete=form.complete_date.data,
            section=form.section.data,
            lecture=form.lecture.data,
            date_added=date.today(),
            user_id=current_user.id
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

        db.session.add(new_proj)
        db.session.commit()
        return redirect(url_for("projects_page"))
    return render_template('add.html', form=form, object="Project")


@app.route('/add-concept', methods=["GET", "POST"])
@login_required
def add_new_concept():
    form = NewConceptForm()
    if form.validate_on_submit():
        new_concept = Concept(
            concept_term=form.concept.data,
            category=form.category.data,
            description=form.description.data,
            date_added=date.today()
        )

        db.session.add(new_concept)
        db.session.commit()
        return redirect(url_for("concepts_page"))
    return render_template('add.html', form=form, object="Concept")


@app.route('/add-library', methods=["GET", "POST"])
@login_required
def add_new_library():
    form = NewLibraryForm()
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        new_lib = Library(
            name=form.name.data,
            description=form.description.data,
            doc_link=form.doc_link.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_lib)

        form_concepts = form.concepts.data
        form_concepts.append(form.name.data)

        if len(form_concepts) > 0:
            for concept_name in form_concepts:
                concept = Concept.query.filter_by(concept_term=concept_name.lower()).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
                        category='library',
                        date_added=date.today()
                    )

                    db.session.add(concept)

                new_lib.concepts.append(concept)

        db.session.add(new_lib)
        db.session.commit()
        return redirect(url_for("libraries_page"))
    return render_template('add.html', form=form, object="Library")


@app.route('/add-api', methods=["GET", "POST"])
@login_required
def add_new_api():
    form = NewAPIForm()
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        new_api = API(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            doc_link=form.doc_link.data,
            requires_login=form.requires_login.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_api)

        form_concepts = form.concepts.data
        form_concepts.append(form.name.data)

        if len(form_concepts) > 0:
            for concept_name in form_concepts:
                concept = Concept.query.filter_by(concept_term=concept_name.lower()).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
                        category='api',
                        date_added=date.today()
                    )

                    db.session.add(concept)

                new_api.concepts.append(concept)

        db.session.add(new_api)
        db.session.commit()
        return redirect(url_for("apis_page"))
    return render_template('add.html', form=form, object="API")


@app.route('/add-tool', methods=["GET", "POST"])
@login_required
def add_new_tool():
    form = NewToolForm()
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        new_tool = Tool(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            doc_link=form.doc_link.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_tool)

        form_concepts = form.concepts.data
        form_concepts.append(form.name.data)

        if len(form_concepts) > 0:
            for concept_name in form_concepts:
                concept = Concept.query.filter_by(concept_term=concept_name.lower()).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
                        category='tool',
                        date_added=date.today()
                    )

                    db.session.add(concept)

                new_tool.concepts.append(concept)

        db.session.add(new_tool)
        db.session.commit()
        return redirect(url_for("tools_page"))
    return render_template('add.html', form=form, object="Tool")


@app.route('/add-resource', methods=["GET", "POST"])
@login_required
def add_new_resource():
    form = NewResourceForm()
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        new_resource = Resource(
            name=form.name.data,
            description=form.description.data,
            type=form.type.data,
            resource_url=form.resource_url.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_resource)

        form_concepts = form.concepts.data
        form_concepts.append(form.name.data)

        if len(form_concepts) > 0:
            for concept_name in form_concepts:
                concept = Concept.query.filter_by(concept_term=concept_name.lower()).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
                        category='resource',
                        date_added=date.today()
                    )

                    db.session.add(concept)

                new_resource.concepts.append(concept)

        db.session.add(new_resource)
        db.session.commit()
        return redirect(url_for("resources_page"))
    return render_template('add.html', form=form, object="Resource")


##################################### READ PAGES ########################################


@app.route('/courses/<int:num>')
@login_required
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


@app.route('/projects/<int:num>')
@login_required
def project_detail(num):
    target_project = db.get_or_404(Project, num)
    proj_concepts = []

    for concept in target_project.concepts:
        proj_concepts.append(concept.concept_term)

    # # Sort descending
    # sorted_concepts = dict(
    #     sorted(course_concepts.items(), key=lambda item: item[1], reverse=True))

    return render_template('project-detail.html', project=target_project, concepts=proj_concepts)


##################################### UPDATE PAGES ########################################


@app.route('/courses/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_course(num):
    course_to_update = db.session.execute(db.select(Course).where(Course.id == num)).scalar()
    form = NewCourseForm(obj=course_to_update)

    if request.method == "POST":
        if form.validate_on_submit():
            course_to_update.title = form.title.data
            course_to_update.platform = form.platform.data
            course_to_update.url = form.url.data
            course_to_update.instructor = form.instructor.data
            course_to_update.content_hours = form.content_hours.data
            course_to_update.has_cert = form.has_cert.data

            if form.start_date.data:
                course_to_update.start = form.start_date.data
            if form.complete_date.data:
                course_to_update.complete = form.complete_date.data

            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("course_detail", num=num))
    return render_template('update.html', form=form, object="Course")