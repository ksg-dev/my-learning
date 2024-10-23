from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, Float, Date, DateTime
from app import app, db, login_manager
import datetime
from typing import List
from flask_login import UserMixin
import sqlalchemy as sa

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#################### JOIN TABLES ####################
# Join table for projects and concepts
project_concept = db.Table(
    "project_concept",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)

# Join table for codelinks and concepts
codelink_concept = db.Table(
    "codelink_concept",
    db.Column("codelink_id", db.Integer, db.ForeignKey("codelinks.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)

# Join table for users and concepts
user_concept = db.Table(
    "user_concept",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)

# Join table for libraries and concepts
library_concept = db.Table(
    "library_concept",
    db.Column("library_id", db.Integer, db.ForeignKey("libraries.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)

# Join table for apis and concepts
api_concept = db.Table(
    "api_concept",
    db.Column("api_id", db.Integer, db.ForeignKey("apis.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)

# Join table for tools and concepts
tool_concept = db.Table(
    "tool_concept",
    db.Column("tool_id", db.Integer, db.ForeignKey("tools.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)

# Join table for resources and concepts
resource_concept = db.Table(
    "resource_concept",
    db.Column("resource_id", db.Integer, db.ForeignKey("resources.id"), primary_key=True),
    db.Column("concept_id", db.Integer, db.ForeignKey("concepts.id"), primary_key=True)
)


#################### MODEL TABLES ####################
# Create User model for all registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(250))
    name: Mapped[str] = mapped_column(String(1000))
    display_name: Mapped[str] = mapped_column(String(1000))
    # This will act like a List of Project/Course/Lib.etc objects attached to each User.
    # The "user" refers to the user property in the Project/Course/Lib. etc class.
    # Link to Projects
    projects: Mapped[List["Project"]] = relationship(back_populates="user")
    # Link to Events
    events: Mapped[List["Event"]] = relationship(back_populates="user")
    # Link to Courses
    courses: Mapped[List["Course"]] = relationship(back_populates="user")
    # Link to Libraries
    libraries: Mapped[List["Library"]] = relationship(back_populates="user")
    # Link to APIs
    apis: Mapped[List["API"]] = relationship(back_populates="user")
    # Link to Tools/Utils
    tools: Mapped[List["Tool"]] = relationship(back_populates="user")
    # Link to Resources
    resources: Mapped[List["Resource"]] = relationship(back_populates="user")
    # Link to Repos
    repos: Mapped[List["Repository"]] = relationship(back_populates="user")
    # Link to CodeLinks
    codelinks: Mapped[List["CodeLink"]] = relationship(back_populates="user")
    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=user_concept, backref='user')


# Create Repository model to being together events, projects data
class Repository(db.Model):
    __tablename__ = "repos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "repos" refers to the repos property in the User class.
    user: Mapped["User"] = relationship(back_populates="repos")

    # Link to projects
    projects: Mapped[List["Project"]] = relationship(back_populates="repo")

    # Link to codelinks
    codelinks: Mapped[List["CodeLink"]] = relationship(back_populates="repo")

    # Link to events
    events: Mapped[List["Event"]] = relationship(back_populates="repo")


# Create Course model for all planned or completed courses
class Course(db.Model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    platform: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(250), nullable=True)
    instructor: Mapped[str] = mapped_column(String(100))
    start: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    complete: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    content_hours: Mapped[float] = mapped_column(nullable=True)
    has_cert: Mapped[bool] = mapped_column(Boolean)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=True)

    # This will act like a list of Project objects attached to each course
    # The 'course' refers to the course property in the Property class
    projects: Mapped[List["Project"]] = relationship(back_populates="course")

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "courses" refers to the courses property in the User class.
    user: Mapped["User"] = relationship(back_populates="courses")


# Create Projects model for individual projects
class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    assignment_link: Mapped[str] = mapped_column(String(250), nullable=True)
    start: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    complete: Mapped[datetime.date] = mapped_column(Date, nullable=True)


    # Link to Repos
    repo_id: Mapped[int] = mapped_column(Integer, ForeignKey(Repository.id), index=True)
    repo: Mapped["Repository"] = relationship(back_populates="projects")

    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=project_concept, backref='projects')

    section: Mapped[str] = mapped_column(String(100))
    lecture: Mapped[str] = mapped_column(String(100))
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Create Foreign Key, 'courses.id' where courses refers to table name of Courses.
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey(Course.id), index=True)
    # Create reference to Course object. The "projects" refers to the projects property in the Course class.
    course: Mapped["Course"] = relationship(back_populates="projects")

    # This will act like a list of CodeLink objects attached to each project
    # The 'codelink' refers to the project property in the CodeLink class
    codelinks: Mapped[List["CodeLink"]] = relationship(back_populates="project")

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "projects" refers to the projects property in the User class.
    user: Mapped["User"] = relationship(back_populates="projects")


# Create CodeLinks model for tracking permalinks to github code examples
class CodeLink(db.Model):
    __tablename__ = "codelinks"

    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    link: Mapped[str] = mapped_column(String(250), nullable=False)

    # Link to Repos
    repo_id: Mapped[int] = mapped_column(Integer, ForeignKey(Repository.id), index=True)
    repo: Mapped["Repository"] = relationship(back_populates="codelinks")

    # Create Foreign Key, 'projects.id' where projects refers to table name of Projects.
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey(Project.id), index=True)
    # Create reference to Project object. The "codelinks" refers to the codelinks property in the Project class.
    project: Mapped["Project"] = relationship(back_populates="codelinks")

    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=codelink_concept, backref='codelinks')

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "codelinks" refers to the codelinks property in the User class.
    user: Mapped["User"] = relationship(back_populates="codelinks")

# Create Concepts model for tracking key terms and concepts
class Concept(db.Model):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_term: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)


# Create Packages & Libraries model for python libraries/packages
class Library(db.Model):
    __tablename__ = "libraries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    doc_link: Mapped[str] = mapped_column(String(250), nullable=True)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=library_concept, backref='libraries')

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "libraries" refers to the libraries property in the User class.
    user: Mapped["User"] = relationship(back_populates="libraries")


# Create API model for tracking APIs you've used or have already gotten access to
class API(db.Model):
    __tablename__ = "apis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(250), nullable=True)
    doc_link: Mapped[str] = mapped_column(String(250), nullable=True)
    requires_login: Mapped[bool] = mapped_column(Boolean, nullable=True)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=api_concept, backref='apis')

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "apis" refers to the apis property in the User class.
    user: Mapped["User"] = relationship(back_populates="apis")


# Create Tools / Utilities model for various tools and their use
class Tool(db.Model):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(250), nullable=True)
    doc_link: Mapped[str] = mapped_column(String(250), nullable=True)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=tool_concept, backref='tools')

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "tools" refers to the tools property in the User class.
    user: Mapped["User"] = relationship(back_populates="tools")


# Create Resources model to track cheatsheets, diagrams, reference pages - anything not tied to specific project/course
class Resource(db.Model):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=True)
    resource_url: Mapped[str] = mapped_column(String(250), nullable=True)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=resource_concept, backref='resources')

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "resources" refers to the resources property in the User class.
    user: Mapped["User"] = relationship(back_populates="resources")


# Create GitHub Events model for api events data
class Event(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(250))
    commits: Mapped[int] = mapped_column(Integer, nullable=True)
    create_type: Mapped[str] = mapped_column(String(250), nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime())

    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id), index=True)
    # Create reference to the User object. The "events" refers to the events property in the User class.
    user: Mapped["User"] = relationship(back_populates="events")

    # Create Foreign Key, "repo.id" the repos refers to the tablename of Repo.
    repo_id: Mapped[int] = mapped_column(Integer, ForeignKey(Repository.id), index=True)
    # Create reference to the Repository object. The "events" refers to the events property in the Repository class.
    repo: Mapped["Repository"] = relationship(back_populates="events")






# Create table schema in db w app context
with app.app_context():
    db.create_all()


