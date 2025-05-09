import datetime
import json
import random

from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, current_app
from flask_bootstrap import Bootstrap5
from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, func
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from flask_socketio import SocketIO
from flask_ckeditor.utils import cleanify
from dotenv import load_dotenv

import time
import threading
import os
import calendar
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequestKeyError
from flask_login import login_user, current_user, logout_user, login_required


from app import app, db
from app.models import User, Course, Project, CodeLink, Concept, Library, API, Tool, Resource, Event, Repository
from app.forms import (RegisterForm, LoginForm,
                       NewCourseForm, NewProjectForm, NewCodeLinkForm, NewConceptForm, QuickAddConcept,
                       NewAPIForm, NewLibraryForm, NewToolForm, NewResourceForm,
                       DeleteForm, UploadForm, UpdateProjectForm, PasswordReset)
from app.github import GetGitHub
# from app.stats import Dashboard
from app.dashboard import Dashboard
from app.upload import upload_courses, upload_projects, upload_libraries, upload_apis, upload_tools, upload_resources, upload_codelinks
from app.upload_dicts import course_params, project_params, library_params, api_params, tool_params, resource_params, codelink_params
from app.tree import make_tree

bootstrap = Bootstrap5(app)
ckeditor = CKEditor(app)

load_dotenv()

DB_URI = os.environ["DB_URI"]

GH_API_URL = "https://api.github.com/"
GH_USERNAME = os.environ["GITHUB_USERNAME"]

# To show resource categories across pages, pass to index as badge=dict
# 'category or status in db': ['text to appear on badge', 'color of icon', 'badge icon']
resource_categories = {
    'cheatsheet': ['Cheatsheet', 'darkslateblue', 'ri-spy-fill'],
    'diagram': ['Diagram', 'blueviolet', 'ri-flow-chart'],
    'quickref': ['Quick Reference', 'deepskyblue', 'ri-bookmark-fill'],
    'template': ['Template', 'orchid', 'ri-layout-2-fill'],
    'code': ['Code', 'darkslategrey', 'ri-terminal-box-fill'],
    'other': ['Other', 'chocolate', 'ri-attachment-2']
}

# To show concept categories across pages, pass to index as badge=dict
# 'category or status in db': ['text to appear on badge', 'color of icon', 'badge icon']
concept_categories = {
    'library': ['Library', 'orangered', 'bi-box-fill'],
    'api': ['API', 'darkcyan', 'ri-key-fill'],
    'tool': ['Tool', 'darkslategrey', 'bi-tools'],
    'resource': ['Resource', 'maroon', 'bx bx-plus-medical'],
    'topic': ['Topic', 'mediumslateblue', 'ri-discuss-fill'],
    'function': ['Function', 'fuchsia', 'bx bx-code-curly'],
    'research': ['Investigate', 'olivedrab', 'ri-spy-fill'],
    'other': ['Other', 'orange', 'ri-draft-fill']
}

# course statuses, pass to index as badge=dict
# 'category or status in db': ['text to appear on badge', 'badge class-starting bg', 'badge icon-starting bi']
course_statuses = {
    'not-started': ['Not Started', 'bg-secondary', 'bi-hourglass'],
    'in-progress': ['In Progress', 'bg-warning text-dark', 'bi-arrow-repeat'],
    'complete': ['Complete', 'bg-success', 'bi-check-circle']
}

# To show tool/utility categories across pages, pass to index as badge=dict
# 'category or status in db': ['text to appear on badge', 'color of icon', 'badge icon']
tool_categories = {
    'essentials': ['Code Essentials', 'green', 'ri-seedling-fill'],
    'gamedev': ['Game Development', 'goldenrod', 'ri-game-fill'],
    'code-execution': ['Code Execution', 'darkslategrey', 'ri-terminal-box-fill'],
    'data-science': ['Data Science', 'firebrick', 'ri-microscope-fill'],
    'documentation': ['Documentation', 'cornflowerblue', 'ri-quill-pen-fill'],
    'styling': ['Styling & UI', 'hotpink', 'ri-palette-fill'],
    'auth': ['Authentication', 'darkviolet', 'ri-shield-keyhole-fill'],
    'storage': ['Storage', 'coral', 'ri-database-2-fill'],
    'hosting': ['Hosting & Deployment', 'dodgerblue', 'ri-earth-fill'],
    'planning': ['Planning & Architecture', 'darkcyan', 'ri-compasses-2-fill'],
    'other': ['Other', 'dimgrey', 'ri-tools-fill']
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
            return redirect(url_for("login"))
        else:
            new_user = User(
                email=entered_email,
                name=form.name.data.title(),
                display_name=form.display_name.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
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
        password = form.password.data

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)

                return redirect(url_for("home"))

            else:
                flash("Email/Password combination incorrect")
                return redirect(url_for("login"))

        else:
            flash("We have no record of that email. Please try again.")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/profile', methods=["POST", "GET"])
@login_required
def profile():
    if request.method == "POST":
        user = db.session.execute(db.select(User).where(User.email == current_user.email)).scalar()
        if user:
            try:
                if current_user.display_name != request.form["fullName"]:
                    user.display_name = request.form["fullName"]
                if current_user.name != request.form["company"]:
                    user.name = request.form["company"]
            # Catch error if changing password and no name data passed
            except BadRequestKeyError:
                # Just using random word as verification for now to fix non-hashed stored pw
                if request.form["password"] == "bananas":
                    if request.form["newpassword"] == request.form["renewpassword"]:
                        user.password = generate_password_hash(request.form["newpassword"], method='pbkdf2:sha256', salt_length=8)

        db.session.commit()
    return render_template("profile.html")

@app.route('/resetpassword', methods=["POST", "GET"])
def secret_password_reset():
    form = PasswordReset()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user and form.codeword.data == 'bananas':
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("secret_password.html", form=form)


@app.route('/faq')
def faq():
    return render_template("faq.html")


@app.route('/contact')
def contact():
    return render_template("contact.html")


@app.route('/')
@app.route('/index')
@login_required
def home():
    # Create Dashboard Object - refresh events
    dashboard = Dashboard(user=current_user.name, user_id=current_user.id)
    github = GetGitHub(user=current_user.name, user_id=current_user.id)
    now = datetime.utcnow()

    # Build feed
    feed = dashboard.build_feed(github.fetch_events())

    # Get Course stats
    course_stats = dashboard.get_course_stats()

    # Query db for repo activity, convert to python list
    get_repos = db.session.execute(db.select(Repository).filter_by(user_id=current_user.id)).scalars().all()
    repos = [repo for repo in get_repos]

    # Get language data from json dumps
    with open('repo-languages.json', 'r') as file:
        lang_data = json.load(file)

    language_chart_data = dashboard.get_lang_chart(lang_data)

    # Get commit stats for two charts
    commits = github.clean_commit_data()

    get_chart_data = dashboard.get_commit_chart_data(commits)
    get_commit_stats = dashboard.get_commit_stats(commits)

    # months = get_chart_data.index.tolist()
    # months = get_chart_data.index.strftime('%d/%m/%Y').tolist()
    # print(f"MONTHS: {months}")
    # values = get_chart_data.repo.tolist()
    # values = get_chart_data.values.tolist()
    # print(f"VALUES: {values}")

    # labels = [calendar.month_abbr[i] for i in months]
    # print(f"LABELS: {labels}")
    # data = [int(i) for i in values]
    # print(f"DATA: {data}")

    sample_data = [
        {
            'x': '05/06/2014',
            'y': 54
        },
        {
            'x': '05/08/2014',
            'y': 36
        },
        {
            'x': '05/10/2014',
            'y': 65
        },
        {
            'x': '05/12/2014',
            'y': 43
        },
        {
            'x': '05/14/2014',
            'y': 62
        },
    ]

    sample2 = [
        {
            'name': 'my-learning',
            'data': [
                ['03/31/2025', 11],
                ['02/28/2025', 5],
                ['01/31/2025', 17],
                ['12/31/2024', 9],
                ['11/30/2024', 3]
            ]
        },
        {
            'name': 'small-projects',
            'data': [
                ['03/31/2025', 4],
                ['02/28/2025', 15],
                ['01/31/2025', 8],
                ['12/31/2024', 3],
                ['11/30/2024', 17]
            ]
        },
        {
            'name': 'voc-tool',
            'data': [
                ['07/31/2024', 5],
                ['08/31/2024', 16],
                ['09/30/2024', 1],
                ['12/31/2024', 9],
                ['11/30/2024', 3]
            ]
        },
        {
            'name': 'dashboard',
            'data': [
                ['07/31/2024', 2],
                ['08/31/2024', 15],
                ['09/30/2024', 4],
                ['10/31/2024', 1],
                ['11/30/2024', 13]
            ]
        },

    ]

    # Query db for all projects. Convert to python list
    get_projects = db.session.execute(db.select(Project).where(Project.user_id == current_user.id)).scalars().all()
    projects = [project for project in get_projects]
    proj_count = len(projects)

    context = {
        # "months": months,
        # "data": values,
        "data": get_chart_data,
        "lang_data": language_chart_data,
        "my_stats": get_commit_stats,
        "now": now,
        "activity": feed,
        "my_repos": repos,
        "my_courses": course_stats,
        "my_projects": projects,
        "project_count": proj_count
    }

    return render_template('index.html', **context)

################################## TASK THREAD ##############################################
from app.tasks import TaskThread

tasks = {}


@app.route('/start_task', methods=["POST"])
def start_task():
    # github = GetGitHub(user=current_user.name, user_id=current_user.id)
    task_id = str(random.randint(1000, 9999))
    context = current_app._get_current_object()
    task_thread = TaskThread(task_id, context)
    tasks[task_id] = task_thread
    task_thread.start()
    return jsonify({'task_id': task_id})


@app.route('/get_progress/<task_id>')
def get_progress(task_id):
    if task_id not in tasks:
        return jsonify({'error': 'Task not found'}), 404

    task = tasks[task_id]
    progress = task.get_progress()
    result = task.get_result()
    if progress > 99:
        del tasks[task_id]
        return jsonify({'progress': progress, 'result': result})
    return jsonify({'progress': progress, 'result': result})


##################################### LANDING PAGES ########################################
@app.route('/concepts', methods=["GET", "POST"])
@login_required
def concepts_page():
    # Get concepts
    get_concepts = db.session.execute(db.select(Concept).order_by(func.lower(Concept.concept_term))).scalars().all()
    get_research = db.session.execute(db.select(Concept)
                                      .where(Concept.category == "research")
                                      .order_by(Concept.date_added.desc())).scalars().all()
    concepts = [concept for concept in get_concepts]
    research_list = [concept for concept in get_research]

    form = QuickAddConcept()

    if request.method == "POST":
        if form.validate_on_submit():
            # check if concept in db already
            term = form.concept_term.data
            if term.lower() not in concepts:

                new_concept = Concept(
                    concept_term=form.concept_term.data,
                    category='research',
                    date_added=date.today()
                )

                db.session.add(new_concept)
                db.session.commit()

                return redirect(url_for("concepts_page"))
            else:
                flash("Concept or term already exists")
        else:
            print(f"Form Error: {form.errors}")

    return render_template('concepts.html', concepts=concepts, badge=concept_categories, research=research_list, form=form)


@app.route('/courses')
@login_required
def courses_page():
    # Get courses
    get_courses = db.session.execute(db.select(Course).filter_by(user_id=current_user.id)).scalars().all()
    courses = [course for course in get_courses]

    # Get course stats dict from Dashboard
    dashboard = Dashboard(user_id=current_user.id, user=current_user.name)
    course_stats = dashboard.get_course_stats()

    return render_template('courses.html', courses=courses, course_badge=course_statuses, my_courses=course_stats)


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

    top_10_list = list(sorted_concepts)[:10]
    top_10 = {concept: count for (concept, count) in sorted_concepts.items() if concept in top_10_list}

    return render_template('projects.html', projects=projects, top_concepts=top_10)


@app.route('/codelinks')
@login_required
def codelinks_page():
    # Get codelinks
    get_codelinks = db.session.execute(db.select(CodeLink).filter_by(user_id=current_user.id)).scalars().all()
    codelinks = [codelink for codelink in get_codelinks]

    top_concepts = {}

    # Add all concepts to dict as key, and count of occurrence as value
    for link in get_codelinks:
        for concept in link.concepts:
            if concept.concept_term in top_concepts:
                top_concepts[concept.concept_term] += 1
            else:
                top_concepts[concept.concept_term] = 1

    # Sort descending
    sorted_concepts = dict(
        sorted(top_concepts.items(), key=lambda item: item[1], reverse=True))

    return render_template('codelinks.html', codelinks=codelinks, top_concepts=top_concepts)


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

    return render_template('tools.html', tools=tools, badge=tool_categories)


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
            name=form.name.data,
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

        if form.complete_date.data:
            new_course.status = 'complete'

        elif form.start_date.data:
            new_course.status = 'in-progress'

        else:
            new_course.status = 'not-started'

        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for("courses_page"))
    return render_template('add.html', form=form, object="Course", course_badge=course_statuses)


@app.route('/add-project', methods=["GET", "POST"])
@login_required
def add_new_project(course_id=None):
    form = NewProjectForm()
    repos = db.session.execute(db.select(Repository).where(Repository.user_id == current_user.id)).scalars().all()
    form.repo.choices = [(g.id, g.name) for g in repos]
    if course_id:
        target_course = db.session.execute(db.select(Course).where(Course.id == course_id)).scalar()
        form.course.data = target_course
    else:
        form.course.choices = [(g.id, g.name) for g in Course.query.all()]

    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        new_proj = Project(
            name=form.name.data,
            repo_id=form.repo.data,
            description=form.description.data,
            assignment_link=form.assignment_link.data,
            path=form.path.data,
            course_id=form.course.data,
            start=form.start_date.data,
            last_updated=form.last_updated_date.data,
            section=form.section.data,
            lecture=form.lecture.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_proj)

        form_concepts = form.concepts.data

        if len(form_concepts) > 0:
            for concept_name in form_concepts:
                if concept_name.lower() not in all_concepts:
                    concept = Concept(
                        concept_term=concept_name,
                        date_added=date.today()
                    )

                    db.session.add(concept)

                concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                new_proj.concepts.append(concept)

        db.session.add(new_proj)
        db.session.commit()
        return redirect(url_for("projects_page"))
    return render_template('add.html', form=form, object="Project")


@app.route('/add-codelink', methods=["GET", "POST"])
@login_required
def add_new_codelink():
    form = NewCodeLinkForm()
    repos = db.session.execute(db.select(Repository).where(Repository.user_id == current_user.id)).scalars().all()
    projects = db.session.execute(db.select(Project).where(Project.user_id == current_user.id)).scalars().all()
    # form.repo.choices = [(g.id, g.name) for g in repos]
    form.project.choices = [(g.id, g.name) for g in projects]
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    if form.validate_on_submit():
        frags = form.link.data.split('/')
        target_repo = frags[4]
        get_repo = db.session.execute(db.select(Repository).where(Repository.name == target_repo)).scalar()

        new_codelink = CodeLink(
            name=form.name.data,
            link=form.link.data,
            project_id=form.project.data,
            repo_id=get_repo.id,
            user_id=current_user.id
        )

        db.session.add(new_codelink)

        form_concepts = form.concepts.data

        if len(form_concepts) > 0:
            for concept_name in form_concepts:
                if concept_name.lower() not in all_concepts:
                    concept = Concept(
                        concept_term=concept_name,
                        date_added=date.today()
                    )

                    db.session.add(concept)

                concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                new_codelink.concepts.append(concept)

        db.session.add(new_codelink)
        db.session.commit()
        return redirect(url_for("codelinks_page"))
    return render_template('add.html', form=form, object="CodeLink")

@app.route('/add-concept', methods=["GET", "POST"])
@login_required
def add_new_concept():
    form = NewConceptForm()
    if form.validate_on_submit():
        new_concept = Concept(
            concept_term=form.concept_term.data,
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

        # If name in list, fetch and check for category, if none - update
        if new_lib.name.lower() in all_concepts:
            concept_check = db.session.execute(
                db.select(Concept).where(func.lower(Concept.concept_term) == func.lower(new_lib.name))).scalar()

            if not concept_check.category:
                concept_check.category = "library"

                db.session.add(concept_check)

                # add asset name to list of referenced concepts
                new_lib.concepts.append(concept_check)

        # if name not in all_concepts, add new to db
        else:
            add_asset = Concept(
                concept_term=new_lib.name,
                desscription=new_lib.description,
                category='library',
                date_added=date.today()
            )

            db.session.add(add_asset)

            # add asset name to list of referenced concepts
            new_lib.concepts.append(add_asset)

        #   Can't use len here, form_concepts populates [''] when field left blank
        if form_concepts[0] != '':
            for concept_name in form_concepts:
                concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
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

        # If name in list, fetch and check for category, if none - update
        if new_api.name.lower() in all_concepts:
            concept_check = db.session.execute(
                db.select(Concept).where(func.lower(Concept.concept_term) == func.lower(new_api.name))).scalar()

            if not concept_check.category:
                concept_check.category = "api"

                db.session.add(concept_check)

                # add asset name to list of referenced concepts
                new_api.concepts.append(concept_check)

        # if name not in all_concepts, add new to db
        else:
            add_asset = Concept(
                concept_term=new_api.name,
                description=new_api.description,
                category='api',
                date_added=date.today()
            )

            db.session.add(add_asset)

            # add asset name to list of referenced concepts
            new_api.concepts.append(add_asset)

        #   Can't use len here, form_concepts populates [''] when field left blank
        if form_concepts[0] != '':
            for concept_name in form_concepts:
                concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
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
            type=form.type.data,
            url=form.url.data,
            doc_link=form.doc_link.data,
            date_added=date.today(),
            user_id=current_user.id
        )

        db.session.add(new_tool)

        form_concepts = form.concepts.data

        # If name in list, fetch and check for category, if none - update
        if new_tool.name.lower() in all_concepts:
            concept_check = db.session.execute(
                db.select(Concept).where(func.lower(Concept.concept_term) == func.lower(new_tool.name))).scalar()

            if not concept_check.category:
                concept_check.category = "tool"

                db.session.add(concept_check)

                # add asset name to list of referenced concepts
                new_tool.concepts.append(concept_check)

        # if name not in all_concepts, add new to db
        else:
            add_asset = Concept(
                concept_term=new_tool.name,
                description=new_tool.description,
                category='tool',
                date_added=date.today()
            )

            db.session.add(add_asset)

            # add asset name to list of referenced concepts
            new_tool.concepts.append(add_asset)

        #   Can't use len here, form_concepts populates [''] when field left blank
        if form_concepts[0] != '':
            for concept_name in form_concepts:
                concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
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

        #   Can't use len here, form_concepts populates [''] when field left blank
        if form_concepts[0] != '':
            for concept_name in form_concepts:
                concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                if not concept:
                    concept = Concept(
                        concept_term=concept_name,
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

    return render_template('course-detail.html',
                           course=target_course,
                           projects=all_projects,
                           top_concepts=sorted_concepts,
                           course_badge=course_statuses)


@app.route('/projects/<int:num>')
@login_required
def project_detail(num):
    target_project = db.get_or_404(Project, num)
    proj_concepts = []
    proj_codelinks = db.session.execute(db.select(CodeLink).where(CodeLink.project_id == num)).scalars().all()

    for concept in target_project.concepts:
        proj_concepts.append(concept)

    return render_template('project-detail.html',
                           project=target_project,
                           concepts=proj_concepts,
                           concept_badge=concept_categories,
                           codelinks=proj_codelinks)


@app.route('/concepts/<int:num>')
@login_required
def concept_detail(num):
    target_concept = db.session.execute(db.select(Concept).where(Concept.id == num)).scalar()

    libraries = [library for library in target_concept.libraries]
    projects = [project for project in target_concept.projects]
    codelinks = [codelink for codelink in target_concept.codelinks]
    apis = [api for api in target_concept.apis]
    tools = [tool for tool in target_concept.tools]
    resources = [resource for resource in target_concept.resources]

    return render_template('concept-detail.html',
                           concept=target_concept,
                           projects=projects,
                           libraries=libraries,
                           codelinks=codelinks,
                           apis=apis,
                           tools=tools,
                           resources=resources,
                           resource_badge=resource_categories,
                           tool_badge=tool_categories,
                           concept_badge=concept_categories)


@app.route('/libraries/<int:num>')
@login_required
def library_detail(num):
    target_library = db.session.execute(db.select(Library).where(Library.id == num)).scalar()
    library_concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(target_library.name)).first()

    projects = [project for project in library_concept.projects]
    codelinks = [codelink for codelink in library_concept.codelinks]
    resources = [resource for resource in library_concept.resources]

    return render_template('library-detail.html',
                           library=target_library,
                           projects=projects,
                           codelinks=codelinks,
                           resources=resources,
                           resource_badge=resource_categories,
                           concept_badge=concept_categories)


@app.route('/apis/<int:num>')
@login_required
def api_detail(num):
    target_api = db.session.execute(db.select(API).where(API.id == num)).scalar()
    api_concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(target_api.name)).first()

    projects = [project for project in api_concept.projects]
    codelinks = [codelink for codelink in api_concept.codelinks]
    resources = [resource for resource in api_concept.resources]

    return render_template('api-detail.html',
                           api=target_api,
                           projects=projects,
                           codelinks=codelinks,
                           resources=resources,
                           resource_badge=resource_categories,
                           concept_badge=concept_categories)


@app.route('/tools/<int:num>')
@login_required
def tool_detail(num):
    target_tool = db.session.execute(db.select(Tool).where(Tool.id == num)).scalar()
    tool_concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(target_tool.name)).first()

    projects = [project for project in tool_concept.projects]
    codelinks = [codelink for codelink in tool_concept.codelinks]
    resources = [resource for resource in tool_concept.resources]

    return render_template('tool-detail.html',
                           tool=target_tool,
                           projects=projects,
                           codelinks=codelinks,
                           resources=resources,
                           resource_badge=resource_categories,
                           tool_badge=tool_categories,
                           concept_badge=concept_categories)

# TODO: Maybe add field to embed code blocks or attachments, not just through link?
@app.route('/resources/<int:num>')
@login_required
def resource_detail(num):
    target_resource = db.session.execute(db.select(Resource).where(Resource.id == num)).scalar()
    resource_concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(target_resource.name)).first()

    return render_template('resource-detail.html',
                           resource=target_resource,
                           resource_badge=resource_categories,
                           tool_badge=tool_categories,
                           concept_badge=concept_categories)


##################################### UPDATE PAGES ########################################


@app.route('/courses/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_course(num):
    course_to_update = db.session.execute(db.select(Course).where(Course.id == num)).scalar()
    form = NewCourseForm(obj=course_to_update)

    if request.method == "POST":
        if form.validate_on_submit():
            course_to_update.name = form.name.data
            course_to_update.platform = form.platform.data
            course_to_update.url = form.url.data
            course_to_update.instructor = form.instructor.data
            course_to_update.content_hours = form.content_hours.data
            course_to_update.has_cert = form.has_cert.data

            if form.start_date.data:
                course_to_update.start = form.start_date.data
            if form.complete_date.data:
                course_to_update.complete = form.complete_date.data

            if course_to_update.complete:
                course_to_update.status = 'complete'
            elif course_to_update.start:
                course_to_update.status = 'in-progress'
            else:
                course_to_update.status = 'not-started'

            print(course_to_update.status)

            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("course_detail", num=num, course_badge=course_statuses))
    return render_template('update.html', form=form, object="Course")


@app.route('/projects/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_project(num):
    project_to_update = db.session.execute(db.select(Project).where(Project.id == num)).scalar()
    form = UpdateProjectForm()
    concepts_list = [concept.concept_term for concept in project_to_update.concepts]

    if request.method == "GET":
        form.name.data = project_to_update.name
        form.description.data = project_to_update.description
        form.assignment_link.data = project_to_update.assignment_link
        form.path.data = project_to_update.path
        form.section.data = project_to_update.section
        form.lecture.data = project_to_update.lecture
        form.concepts.data = concepts_list

    elif request.method == "POST":
        if form.validate_on_submit():
            project_to_update.name = form.name.data
            project_to_update.description = form.description.data
            project_to_update.assignment_link = form.assignment_link.data
            project_to_update.path = form.path.data
            project_to_update.section = form.section.data
            project_to_update.lecture = form.lecture.data

            form_concepts = form.concepts.data
            lower = [concept.lower() for concept in concepts_list]

            # Loop through list of concepts on form - if not on existing list of concepts, add
            for concept_name in form_concepts:
                if concept_name.lower() not in lower:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                    if not concept:
                        concept = Concept(
                            concept_term=concept_name,
                            date_added=date.today()
                        )

                        db.session.add(concept)

                    project_to_update.concepts.append(concept)

            lower_form_list = [concept.lower() for concept in form_concepts]
            # Check for concept removal
            for concept_name in concepts_list:
                if concept_name.lower() not in lower_form_list:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                    project_to_update.concepts.remove(concept)

            if form.start_date.data:
                project_to_update.start = form.start_date.data
            if form.last_updated.data:
                project_to_update.last_updated = form.last_updated.data

            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("project_detail", num=num))
    return render_template('update.html', form=form, object="Project")


@app.route('/concepts/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_concept(num):
    concept_to_update = db.session.execute(db.select(Concept).where(Concept.id == num)).scalar()
    form = NewConceptForm(obj=concept_to_update)

    if request.method == "POST":
        if form.validate_on_submit():
            concept_to_update.concept_term = form.concept_term.data
            concept_to_update.category = form.category.data
            concept_to_update.description = form.description.data


            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("concept_detail", num=num, concept_badge=concept_categories))
    return render_template('update.html', form=form, object="Concept")


@app.route('/libraries/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_library(num):
    library_to_update = db.session.execute(db.select(Library).where(Library.id == num)).scalar()
    form = NewLibraryForm()
    concepts_list = [concept.concept_term for concept in library_to_update.concepts]

    if request.method == "GET":
        form.name.data = library_to_update.name
        form.description.data = library_to_update.description
        form.doc_link.data = library_to_update.doc_link
        form.concepts.data = concepts_list

    elif request.method == "POST":
        if form.validate_on_submit():
            library_to_update.name = form.name.data
            library_to_update.description = form.description.data
            library_to_update.doc_link = form.doc_link.data

            form_concepts = form.concepts.data
            lower = [concept.lower() for concept in concepts_list]

            # Loop through list of concepts on form - if not on existing list of concepts, add
            for concept_name in form_concepts:
                if concept_name.lower() not in lower:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                    if not concept:
                        concept = Concept(
                            concept_term=concept_name,
                            date_added=date.today()
                        )

                        db.session.add(concept)

                    library_to_update.concepts.append(concept)

            lower_form_list = [concept.lower() for concept in form_concepts]
            # Check for concept removal
            for concept_name in concepts_list:
                if concept_name.lower() not in lower_form_list:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                    library_to_update.concepts.remove(concept)

            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("library_detail", num=num))
    return render_template('update.html', form=form, object="Library")


@app.route('/apis/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_api(num):
    update_target = db.session.execute(db.select(API).where(API.id == num)).scalar()
    form = NewAPIForm()
    concepts_list = [concept.concept_term for concept in update_target.concepts]

    if request.method == "GET":
        form.name.data = update_target.name
        form.description.data = update_target.description
        form.url.data = update_target.url
        form.doc_link.data = update_target.doc_link
        form.requires_login.data = update_target.requires_login
        form.concepts.data = concepts_list

    elif request.method == "POST":
        if form.validate_on_submit():
            update_target.name = form.name.data
            update_target.description = form.description.data
            update_target.url = form.url.data
            update_target.doc_link = form.doc_link.data
            update_target.requires_login = form.requires_login.data

            form_concepts = form.concepts.data
            lower = [concept.lower() for concept in concepts_list]

            # Loop through list of concepts on form - if not on existing list of concepts, add
            for concept_name in form_concepts:
                if concept_name.lower() not in lower:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                    if not concept:
                        concept = Concept(
                            concept_term=concept_name,
                            date_added=date.today()
                        )

                        db.session.add(concept)

                    update_target.concepts.append(concept)

            lower_form_list = [concept.lower() for concept in form_concepts]
            # Check for concept removal
            for concept_name in concepts_list:
                if concept_name.lower() not in lower_form_list:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                    update_target.concepts.remove(concept)

            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("api_detail", num=num))
    return render_template('update.html', form=form, object="API")


@app.route('/tools/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_tool(num):
    update_target = db.session.execute(db.select(Tool).where(Tool.id == num)).scalar()
    form = NewToolForm()
    concepts_list = [concept.concept_term for concept in update_target.concepts]

    if request.method == "GET":
        form.name.data = update_target.name
        form.description.data = update_target.description
        form.type.data = update_target.type
        form.url.data = update_target.url
        form.doc_link.data = update_target.doc_link
        form.concepts.data = concepts_list

    elif request.method == "POST":
        if form.validate_on_submit():
            update_target.name = form.name.data
            update_target.description = form.description.data
            update_target.type = form.type.data
            update_target.url = form.url.data
            update_target.doc_link = form.doc_link.data

            form_concepts = form.concepts.data
            lower = [concept.lower() for concept in concepts_list]

            # Loop through list of concepts on form - if not on existing list of concepts, add
            for concept_name in form_concepts:
                if concept_name.lower() not in lower:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                    if not concept:
                        concept = Concept(
                            concept_term=concept_name,
                            date_added=date.today()
                        )

                        db.session.add(concept)

                    update_target.concepts.append(concept)

            lower_form_list = [concept.lower() for concept in form_concepts]
            # Check for concept removal
            for concept_name in concepts_list:
                if concept_name.lower() not in lower_form_list:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                    update_target.concepts.remove(concept)


            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("tool_detail", num=num))
    return render_template('update.html', form=form, object="Tool")


@app.route('/resources/<int:num>/update', methods=["GET", "POST"])
@login_required
def update_resource(num):
    update_target = db.session.execute(db.select(Resource).where(Resource.id == num)).scalar()
    form = NewResourceForm()
    concepts_list = [concept.concept_term for concept in update_target.concepts]

    if request.method == "GET":
        form.name.data = update_target.name
        form.description.data = update_target.description
        form.type.data = update_target.type
        form.resource_url.data = update_target.resource_url
        form.concepts.data = concepts_list

    elif request.method == "POST":
        if form.validate_on_submit():
            update_target.name = form.name.data
            update_target.description = form.description.data
            update_target.type = form.type.data
            update_target.resource_url = form.resource_url.data

            form_concepts = form.concepts.data
            lower = [concept.lower() for concept in concepts_list]

            # Loop through list of concepts on form - if not on existing list of concepts, add
            for concept_name in form_concepts:
                if concept_name.lower() not in lower:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()
                    if not concept:
                        concept = Concept(
                            concept_term=concept_name,
                            date_added=date.today()
                        )

                        db.session.add(concept)

                    update_target.concepts.append(concept)

            lower_form_list = [concept.lower() for concept in form_concepts]
            # Check for concept removal
            for concept_name in concepts_list:
                if concept_name.lower() not in lower_form_list:
                    concept = Concept.query.filter(
                        func.lower(Concept.concept_term) == func.lower(concept_name)).first()

                    update_target.concepts.remove(concept)


            db.session.commit()

            flash("Success! Record Updated.")

            return redirect(url_for("resources_page"))
    return render_template('update.html', form=form, object="Resource")


##################################### DELETE PAGES ########################################


@app.route('/courses/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_course(num):
    course_to_delete = db.session.execute(db.select(Course).where(Course.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(course_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("courses_page"))
    return render_template("delete.html", form=form, object="Course", item=course_to_delete)


@app.route('/projects/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_project(num):
    project_to_delete = db.session.execute(db.select(Project).where(Project.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(project_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("projects_page"))
    return render_template("delete.html", form=form, object="Project", item=project_to_delete)

# @app.route('/projects/delete-all', methods=["GET", "POST"])
# @login_required
# def bulk_delete_project():
#     form = DeleteForm()
#     rows_deleted = Project.query.all()
#
#     if request.method == "POST":
#         if form.validate_on_submit():
#             try:
#                 Project.query.delete()
#                 db.session.commit()
#             except:
#                 db.session.rollback()
#             return redirect(url_for("projects_page"))
#     return render_template("bulk-delete.html", form=form, object="Project", num_rows=len(rows_deleted))


@app.route('/concepts/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_concept(num):
    concept_to_delete = db.session.execute(db.select(Concept).where(Concept.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(concept_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("concepts_page"))
    return render_template("delete.html", form=form, object="Concept", item=concept_to_delete)

# @app.route('/concepts/delete-all', methods=["GET", "POST"])
# @login_required
# def bulk_delete_concept():
#     form = DeleteForm()
#     rows_deleted = Concept.query.all()
#
#     if request.method == "POST":
#         if form.validate_on_submit():
#             try:
#                 Concept.query.delete()
#                 db.session.commit()
#             except:
#                 db.session.rollback()
#             return redirect(url_for("concepts_page"))
#     return render_template("bulk-delete.html", form=form, object="Concept", num_rows=len(rows_deleted))

@app.route('/libraries/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_library(num):
    library_to_delete = db.session.execute(db.select(Library).where(Library.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(library_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("libraries_page"))
    return render_template("delete.html", form=form, object="Library", item=library_to_delete)


# @app.route('/libraries/delete-all', methods=["GET", "POST"])
# @login_required
# def bulk_delete_library():
#     form = DeleteForm()
#     rows_deleted = Library.query.all()
#
#     if request.method == "POST":
#         if form.validate_on_submit():
#             try:
#                 Library.query.delete()
#                 db.session.commit()
#             except:
#                 db.session.rollback()
#             return redirect(url_for("libraries_page"))
#     return render_template("bulk-delete.html", form=form, object="Library", num_rows=len(rows_deleted))
#

@app.route('/apis/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_api(num):
    api_to_delete = db.session.execute(db.select(API).where(API.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(api_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("apis_page"))
    return render_template("delete.html", form=form, object="API", item=api_to_delete)


@app.route('/tools/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_tool(num):
    tool_to_delete = db.session.execute(db.select(Tool).where(Tool.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(tool_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("tools_page"))
    return render_template("delete.html", form=form, object="Tool", item=tool_to_delete)


@app.route('/resources/<int:num>/delete', methods=["GET", "POST"])
@login_required
def delete_resource(num):
    resource_to_delete = db.session.execute(db.select(Resource).where(Resource.id == num)).scalar()
    form = DeleteForm()

    if request.method == "POST":
        if form.validate_on_submit():
            db.session.delete(resource_to_delete)
            db.session.commit()

            flash("Success! Record Deleted.")

            return redirect(url_for("resources_page"))
    return render_template("delete.html", form=form, object="Resource", item=resource_to_delete)


def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        # NOTE TO SELF: if-statement does not skip over users table, clears all tables,
        # will have to add admin user back via console
        if table != "users":
            print(f"Clear table {table}")
            session.execute(table.delete())
        else:
            print(f"Skipping table {table}")
    session.commit()

##################################### IMPORT PAGES ########################################

@app.route('/courses/upload', methods=["GET", "POST"])
def import_courses():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg, skipped = upload_courses(filename, current_user.id)

        flash(msg)
        if len(skipped) > 0:
            flash(f"{len(skipped)} item(s) skipped due to name duplicate.")
            for i in skipped:
                flash(f"{i} already exists")

        return redirect(url_for('courses_page'))
    return render_template('upload.html', form=form, object="Course", params=course_params)

@app.route('/projects/upload', methods=["GET", "POST"])
def import_projects():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg, skipped = upload_projects(filename, current_user.id)
        no_repo = skipped[0]
        new_course = skipped[1]

        flash(msg)
        if len(no_repo) > 0:
            flash(f"{len(no_repo)} item(s) skipped because repo wasn't found.")

            for i in no_repo:
                flash(f"{i} not found")

        if len(new_course) > 0:
            flash(f"{len(new_course)} course(s) quick added because no course found with that name - their details may need updating")
            for i in new_course:
                flash(f"{i} added")

        return redirect(url_for('projects_page'))
    return render_template('upload.html', form=form, object="Project", params=project_params)


@app.route('/libraries/upload', methods=["GET", "POST"])
def import_libs():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg = upload_libraries(filename, current_user.id)

        flash(msg)

        return redirect(url_for('libraries_page'))
    return render_template('upload.html', form=form, object="Library", params=library_params)


@app.route('/apis/upload', methods=["GET", "POST"])
def import_apis():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg = upload_apis(filename, current_user.id)

        flash(msg)

        return redirect(url_for('apis_page'))
    return render_template('upload.html', form=form, object="API", params=api_params)


@app.route('/tools/upload', methods=["GET", "POST"])
def import_tools():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg = upload_tools(filename, current_user.id)

        flash(msg)

        return redirect(url_for('tools_page'))
    return render_template('upload.html', form=form, object="Tool", params=tool_params)


@app.route('/resources/upload', methods=["GET", "POST"])
def import_resources():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg = upload_resources(filename, current_user.id)

        flash(msg)

        return redirect(url_for('resources_page'))
    return render_template('upload.html', form=form, object="Resource", params=resource_params)


@app.route('/codelinks/upload', methods=["GET", "POST"])
def import_codelinks():
    form = UploadForm()

    if form.validate_on_submit():
        upload = form.upload.data
        filename = secure_filename(upload.filename)
        upload.save(os.path.join(
            app.instance_path, 'imports', filename
        ))

        msg = upload_codelinks(filename, current_user.id)

        flash(msg)

        return redirect(url_for('codelinks_page'))
    return render_template('upload.html', form=form, object="CodeLink", params=codelink_params)


