from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, ForeignKey
from main import app, db

# Create Course table for all completed courses
class Course(db.model):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True)
    platform: Mapped[str] = mapped_column(String(100))
    instructor: Mapped[str] = mapped_column(String(100))


# Create Projects table for individual projects


# Create Terms/Concepts table for tracking key terms and concepts


# Create ...


