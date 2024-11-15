# For handling csv-loaded data
import pandas as pd
import numpy as np
from app import db, app
from app.models import Course, Project, Repository, Concept, Library, API, Tool, Resource, CodeLink
from datetime import date
from sqlalchemy import func
import os



def upload_courses(filename, user_id):
    col_types = {
        'name': str,
        'platform': str,
        'url': str,
        'instructor': str,
        'start': str,
        'complete': str,
        'content_hours': float,
        'has_cert': bool
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):
        # print(row.name)
        # print(row.platform)
        new_course = Course(
            name=row.name,
            platform=row.platform,
            url=row.url,
            instructor=row.instructor,
            start=pd.to_datetime(row.start),
            complete=pd.to_datetime(row.complete),
            content_hours=row.content_hours,
            has_cert=row.has_cert,
            date_added=date.today(),
            user_id=user_id
        )

        if row.complete:
            new_course.status = 'complete'

        elif row.start:
            new_course.status = 'in-progress'

        else:
            new_course.status = 'complete'

        # print(new_course.name)
        db.session.add(new_course)
        db.session.commit()
    # print(data.info())

    response_msg = "Course Import Successful"


    # name = data["name"]
    # start = data["start"]
    # has_cert = data["has_cert"]

    # print(data)
    # print(f"NAME: {name} TYPE: {type(name)}")
    # print(f"NAME: {start} TYPE: {type(start)}")
    # print(f"NAME: {has_cert} TYPE: {type(has_cert)}")

    return(response_msg)


def upload_projects(filename, user_id):
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    col_types = {
        'name': str,
        'description': str,
        'assignment_link': str,
        'start': str,
        'complete': str,
        'section': str,
        'lecture': str,
        'repo': str,
        'concepts': str,
        'course': str,
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):
        # Handle relationship fields
        # Look up Repo
        target_repo = db.session.execute(db.select(Repository).where(Repository.name == row.repo)).scalar()

        # Lookup Course
        target_course = db.session.execute(db.select(Course).where(Course.name == row.course)).scalar()

        new_project = Project(
            name=row.name,
            description=row.description,
            assignment_link=row.assignment_link,
            start=pd.to_datetime(row.start),
            complete=pd.to_datetime(row.complete),
            section=row.section,
            lecture=row.lecture,
            repo=target_repo,
            course=target_course,
            date_added=date.today(),
            user_id=user_id
        )

        db.session.add(new_project)
        # print(new_project.name)
        # print(new_project.repo)
        # print(new_project.course)

        # print(new_project)

        # Concepts
        concepts = row.concepts.split('+')
        # print(concepts)
        for c in concepts:
            if c.lower() not in all_concepts:
                concept = Concept(
                    concept_term=c,
                    date_added=date.today()
                )

                db.session.add(concept)
                # add concept name to all concepts list so subsequent refs don't create dupes
                all_concepts.append(concept.concept_term.lower())
            concept = Concept.query.filter_by(concept_term=c).first()

            new_project.concepts.append(concept)

        db.session.add(new_project)
        db.session.commit()
    response_msg = "Project Upload Successful"

    return response_msg


def upload_libraries(filename, user_id):
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    col_types = {
        'name': str,
        'description': str,
        'doc_link': str,
        'concepts': str,
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):

        new_library = Library(
            name=row.name,
            description=row.description,
            doc_link=row.doc_link,
            date_added=date.today(),
            user_id=user_id
        )

        db.session.add(new_library)

        # Concepts
        concepts = row.concepts.split('+')

        # If name in list, fetch and check for category, if none - update
        if new_library.name.lower() in all_concepts:
            concept_check = db.session.execute(
                db.select(Concept).where(func.lower(Concept.concept_term) == func.lower(new_library.name))).scalar()

            if not concept_check.category:
                concept_check.category = "library"

                db.session.add(concept_check)

            # add asset name to list of referenced concepts
            new_library.concepts.append(concept_check)

        # if name not in all_concepts, add new to db
        else:
            add_asset = Concept(
                concept_term=new_library.name,
                category='library',
                date_added=date.today()
            )

            db.session.add(add_asset)

            # add asset name to list of referenced concepts
            new_library.concepts.append(add_asset)
            # add asset name to all concepts list
            all_concepts.append(new_library.name.lower())


        for c in concepts:
            if c.lower() not in all_concepts:
                concept = Concept(
                    concept_term=c,
                    date_added=date.today()
                )

                db.session.add(concept)
                # # add concept name to all concepts list so subsequent refs don't create dupes
                # all_concepts.append(concept.concept_term.lower())
            concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(c)).first()

            new_library.concepts.append(concept)

        db.session.add(new_library)
        db.session.commit()
    response_msg = "Library Upload Successful"

    return response_msg


def upload_apis(filename, user_id):
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    col_types = {
        'name': str,
        'description': str,
        'url': str,
        'doc_link': str,
        'requires_login': bool,
        'concepts': str,
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):

        new_api = API(
            name=row.name,
            description=row.description,
            url=row.url,
            doc_link=row.doc_link,
            requires_login=row.requires_login,
            date_added=date.today(),
            user_id=user_id
        )

        db.session.add(new_api)

        # Concepts
        concepts = row.concepts.split('+')

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
                category='api',
                date_added=date.today()
            )

            db.session.add(add_asset)

            # add asset name to list of referenced concepts
            new_api.concepts.append(add_asset)
            # add asset name to all concepts list
            all_concepts.append(new_api.name.lower())


        for c in concepts:
            if c.lower() not in all_concepts:
                concept = Concept(
                    concept_term=c,
                    date_added=date.today()
                )

                db.session.add(concept)
            concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(c)).first()

            new_api.concepts.append(concept)

        db.session.add(new_api)
        db.session.commit()
    response_msg = "API Upload Successful"

    return response_msg


def upload_tools(filename, user_id):
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    col_types = {
        'name': str,
        'description': str,
        'url': str,
        'doc_link': str,
        'concepts': str,
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):

        new_tool = Tool(
            name=row.name,
            description=row.description,
            url=row.url,
            doc_link=row.doc_link,
            date_added=date.today(),
            user_id=user_id
        )

        db.session.add(new_tool)

        # Concepts
        concepts = row.concepts.split('+')

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
                category='tool',
                date_added=date.today()
            )

            db.session.add(add_asset)

            # add asset name to list of referenced concepts
            new_tool.concepts.append(add_asset)
            # add asset name to all concepts list
            all_concepts.append(new_tool.name.lower())


        for c in concepts:
            if c.lower() not in all_concepts:
                concept = Concept(
                    concept_term=c,
                    date_added=date.today()
                )

                db.session.add(concept)
            concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(c)).first()

            new_tool.concepts.append(concept)

        db.session.add(new_tool)
        db.session.commit()
    response_msg = "Upload Successful"

    return response_msg


def upload_resources(filename, user_id):
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    col_types = {
        'name': str,
        'description': str,
        'type': str,
        'resource_url': str,
        'concepts': str,
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):

        new_resource = Resource(
            name=row.name,
            description=row.description,
            type=row.type,
            resource_url=row.resource_url,
            date_added=date.today(),
            user_id=user_id
        )

        db.session.add(new_resource)

        # Concepts
        concepts = row.concepts.split('+')


        for c in concepts:
            if c.lower() not in all_concepts:
                concept = Concept(
                    concept_term=c,
                    date_added=date.today()
                )

                db.session.add(concept)
            concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(c)).first()

            new_resource.concepts.append(concept)

        db.session.add(new_resource)
        db.session.commit()
    response_msg = "Resource Upload Successful"

    return response_msg


def upload_codelinks(filename, user_id):
    get_concepts = db.session.execute(db.select(Concept)).scalars().all()
    all_concepts = [concept.concept_term.lower() for concept in get_concepts]

    col_types = {
        'name': str,
        'description': str,
        'link': str,
        'project': str,
        'concepts': str,
    }

    filepath = os.path.join(app.instance_path, 'imports', filename)

    data = pd.read_csv(filepath, dtype=col_types, index_col=False, header=0, skip_blank_lines=True)

    for row in data.itertuples(index=False):

        frags = row.link.split('/')
        target_repo = frags[4]
        get_repo = db.session.execute(db.select(Repository).where(Repository.name == target_repo)).scalar()
        get_project = db.session.execute(db.select(Project).where(Project.name == row.project)).scalar()

        new_codelink = CodeLink(
            name=row.name,
            description=row.description,
            link=row.link,
            project_id=get_project.id,
            repo_id=get_repo.id,
            date_added=date.today(),
            user_id=user_id
        )

        db.session.add(new_codelink)

        # Concepts
        concepts = row.concepts.split('+')


        for c in concepts:
            if c.lower() not in all_concepts:
                concept = Concept(
                    concept_term=c,
                    date_added=date.today()
                )

                db.session.add(concept)
            concept = Concept.query.filter(func.lower(Concept.concept_term) == func.lower(c)).first()

            new_codelink.concepts.append(concept)

        db.session.add(new_codelink)
        db.session.commit()
    response_msg = "CodeLink Upload Successful"

    return response_msg




# upload_projects("test_projects.csv", user_id=1)