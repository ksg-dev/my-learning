from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, Float, Date, DateTime
from app import app, db
import datetime
from typing import List
import sqlalchemy as sa


# Create Course model for all planned or completed courses
class Course(db.Model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    platform: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(250), nullable=True)
    instructor: Mapped[str] = mapped_column(String(100))
    start: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    complete: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    content_hours: Mapped[float] = mapped_column(nullable=True)
    has_cert: Mapped[bool] = mapped_column(Boolean)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # This will act like a list of Project objects attached to each course
    # The 'course' refers to the course property in the Property class
    projects: Mapped[List["Project"]] = relationship(back_populates="course")


# Join table for projects and concepts
project_concept = db.Table(
    "project_concept",
    db.Column("project_id", db.Integer, db.ForeignKey("projects.id"), primary_key=True),
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


# Create Projects model for individual projects
class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_title: Mapped[str] = mapped_column(String(100), nullable=False)
    project_repo: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    assignment_link: Mapped[str] = mapped_column(String(250), nullable=True)
    start: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    complete: Mapped[datetime.date] = mapped_column(Date, nullable=True)


    # Many-to-many relationship to concepts
    concepts: Mapped[List["Concept"]] = relationship('Concept', secondary=project_concept, backref='projects')

    section: Mapped[str] = mapped_column(String(100))
    lecture: Mapped[str] = mapped_column(String(100))
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Create Foreign Key, 'courses.id' where courses refers to table name of Courses.
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey(Course.id), index=True)
    # Create reference to Course object. The "projects" refers to the projects property in the Course class.
    course: Mapped["Course"] = relationship(back_populates="projects")


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


# Create GitHub Events model for api events data
class Events(db.Model):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(250))
    actor: Mapped[str] = mapped_column(String(250))
    ref: Mapped[str] = mapped_column(String(250))
    ref_type: Mapped[str] = mapped_column(String(250))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)


# Create table schema in db w app context
with app.app_context():
    db.create_all()


