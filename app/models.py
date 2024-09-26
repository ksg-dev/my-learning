from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, Float
from app import app, db


# Create Course table for all completed courses
class Course(db.Model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    platform: Mapped[str] = mapped_column(String(100))
    instructor: Mapped[str] = mapped_column(String(100))
    start: Mapped[str] = mapped_column(String(25), nullable=True)
    content_hours: Mapped[float] = mapped_column(nullable=True)
    has_cert: Mapped[bool] = mapped_column(Boolean, nullable=False)


# Create Projects table for individual projects
class Project(db.Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_title: Mapped[str] = mapped_column(String(100), nullable=False)
    project_repo: Mapped[str] = mapped_column(String(100), nullable=False)
    concept: Mapped[str] = mapped_column(String(50), nullable=False)
    course: Mapped[str] = mapped_column(String(100))
    section: Mapped[str] = mapped_column(String(100))
    lecture: Mapped[str] = mapped_column(String(100))


# Create Concepts table for tracking key terms and concepts
class Concept(db.Model):
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    concept_term: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=False)


# Create table schema in db w app context
with app.app_context():
    db.create_all()


