from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, Float, Date
from app import app, db
import datetime
from typing import List
import sqlalchemy as sa


# Create Course table for all planned or completed courses
class Course(db.Model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    platform: Mapped[str] = mapped_column(String(100))
    instructor: Mapped[str] = mapped_column(String(100))
    start: Mapped[str] = mapped_column(String(25), nullable=True)
    content_hours: Mapped[float] = mapped_column(nullable=True)
    has_cert: Mapped[bool] = mapped_column(Boolean)
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # This will act like a list of Project objects attached to each course
    # The 'course' refers to the course property in the Property class
    projects: Mapped[List["Project"]] = relationship(back_populates="course")


# Create Projects table for individual projects
class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_title: Mapped[str] = mapped_column(String(100), nullable=False)
    project_repo: Mapped[str] = mapped_column(String(100), nullable=False)
    concept: Mapped[str] = mapped_column(String(50), nullable=False)

    section: Mapped[str] = mapped_column(String(100))
    lecture: Mapped[str] = mapped_column(String(100))
    date_added: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    # Create Foreign Key, 'courses.id' where courses refers to table name of Courses.
    course_id: Mapped[int] = mapped_column(Integer, ForeignKey(Course.id), index=True)
    # Create reference to Course object. The "projects" refers to the projects property in the Course class.
    course: Mapped["Course"] = relationship(back_populates="projects")



# Create Concepts table for tracking key terms and concepts
class Concept(db.Model):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_term: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=False)


project_concept_m2m = db.Table(
    "project_concept",
    sa.Column("project_id", sa.ForeignKey(Project.id), primary_key=True),
    sa.Column("concept_id", sa.ForeignKey(Concept.id), primary_key=True)
)



# Create table schema in db w app context
with app.app_context():
    db.create_all()


