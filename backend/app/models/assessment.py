import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base


class AssessmentType(str, enum.Enum):
    CIE = "CIE"  # Continuous Internal Evaluation (Tests, Quizzes, Midterms)
    SEE = "SEE"  # Semester End Examination
    ASSIGNMENT = "ASSIGNMENT"
    LAB = "LAB"
    PROJECT = "PROJECT"
    INDIRECT_SURVEY = "INDIRECT_SURVEY"


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "Internal Assessment Test 1", "Semester End Exam"
    assessment_type = Column(Enum(AssessmentType), default=AssessmentType.CIE, nullable=False)
    weight_percentage = Column(Float, default=50.0, nullable=False)  # e.g., 40.0 for CIE, 60.0 for SEE
    max_marks = Column(Float, default=50.0, nullable=False)
    conduct_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    course_offering = relationship("CourseOffering", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    marks = relationship("StudentMark", back_populates="assessment", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(String(50), nullable=False)  # e.g., "Q1a", "Q1b", "Q2"
    max_marks = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    __table_args__ = (UniqueConstraint("assessment_id", "question_number", name="uq_assessment_question_no"),)

    assessment = relationship("Assessment", back_populates="questions")
    co_mappings = relationship("QuestionCoMapping", back_populates="question", cascade="all, delete-orphan")
    marks = relationship("StudentMark", back_populates="question", cascade="all, delete-orphan")


class QuestionCoMapping(Base):
    __tablename__ = "question_co_mappings"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    course_outcome_id = Column(Integer, ForeignKey("course_outcomes.id", ondelete="CASCADE"), nullable=False)
    marks_allocated = Column(Float, nullable=True)  # marks allocated to this CO if question is split
    weight = Column(Float, default=1.0, nullable=False)

    __table_args__ = (UniqueConstraint("question_id", "course_outcome_id", name="uq_question_co"),)

    question = relationship("Question", back_populates="co_mappings")
    course_outcome = relationship("CourseOutcome", back_populates="question_mappings")


class StudentMark(Base):
    __tablename__ = "student_marks"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    marks_obtained = Column(Float, nullable=True)  # None if absent and not zeroed
    is_absent = Column(Boolean, default=False, nullable=False)
    remarks = Column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("question_id", "student_id", name="uq_question_student_mark"),)

    assessment = relationship("Assessment", back_populates="marks")
    question = relationship("Question", back_populates="marks")
    student = relationship("Student", back_populates="marks")


class IndirectAssessment(Base):
    __tablename__ = "indirect_assessments"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False)
    course_outcome_id = Column(Integer, ForeignKey("course_outcomes.id", ondelete="CASCADE"), nullable=False)
    survey_name = Column(String(255), default="Course Exit Survey", nullable=False)
    total_responses = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)
    max_possible_score = Column(Float, default=5.0, nullable=False)
    attainment_percentage = Column(Float, default=0.0, nullable=False)
    conduct_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    course_offering = relationship("CourseOffering", back_populates="indirect_assessments")
    course_outcome = relationship("CourseOutcome", back_populates="indirect_assessments")
