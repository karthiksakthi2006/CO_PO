from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    departments = relationship("Department", back_populates="institution", cascade="all, delete-orphan")
    users = relationship("User", back_populates="institution")
    students = relationship("Student", back_populates="institution")


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    head_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("institution_id", "code", name="uq_inst_dept_code"),)

    institution = relationship("Institution", back_populates="departments")
    programs = relationship("Program", back_populates="department", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="department", cascade="all, delete-orphan")
    users = relationship("User", back_populates="department")
    students = relationship("Student", back_populates="department")


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "2024-2025"
    is_current = Column(Boolean, default=False, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    semesters = relationship("Semester", back_populates="academic_year", cascade="all, delete-orphan")
    course_offerings = relationship("CourseOffering", back_populates="academic_year")


class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Odd Semester 2024 (Sem 5)"
    semester_number = Column(Integer, nullable=False)  # 1 to 8
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)

    academic_year = relationship("AcademicYear", back_populates="semesters")
    course_offerings = relationship("CourseOffering", back_populates="semester")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50), nullable=False)  # e.g., "BTECH-CSE"
    name = Column(String(255), nullable=False)
    degree = Column(String(50), default="B.Tech", nullable=False)
    total_credits = Column(Integer, default=160, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("department_id", "code", name="uq_dept_prog_code"),)

    department = relationship("Department", back_populates="programs")
    courses = relationship("Course", back_populates="program", cascade="all, delete-orphan")
    program_outcomes = relationship("ProgramOutcome", back_populates="program", cascade="all, delete-orphan")
    program_specific_outcomes = relationship("ProgramSpecificOutcome", back_populates="program", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="SET NULL"), nullable=True)
    code = Column(String(50), nullable=False)  # e.g., "CS501"
    name = Column(String(255), nullable=False)
    credits = Column(Integer, default=4, nullable=False)
    semester_number = Column(Integer, default=5, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("department_id", "code", name="uq_dept_course_code"),)

    department = relationship("Department", back_populates="courses")
    program = relationship("Program", back_populates="courses")
    course_outcomes = relationship("CourseOutcome", back_populates="course", cascade="all, delete-orphan")
    course_offerings = relationship("CourseOffering", back_populates="course", cascade="all, delete-orphan")


class CourseOffering(Base):
    __tablename__ = "course_offerings"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semesters.id", ondelete="CASCADE"), nullable=False)
    section = Column(String(10), default="A", nullable=False)
    faculty_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (UniqueConstraint("course_id", "academic_year_id", "semester_id", "section", name="uq_course_offering"),)

    course = relationship("Course", back_populates="course_offerings")
    academic_year = relationship("AcademicYear", back_populates="course_offerings")
    semester = relationship("Semester", back_populates="course_offerings")
    faculty = relationship("User", foreign_keys=[faculty_id])
    enrollments = relationship("Enrollment", back_populates="course_offering", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="course_offering", cascade="all, delete-orphan")
    indirect_assessments = relationship("IndirectAssessment", back_populates="course_offering", cascade="all, delete-orphan")
    attainment_configurations = relationship("AttainmentConfiguration", back_populates="course_offering", cascade="all, delete-orphan")
    attainment_runs = relationship("AttainmentRun", back_populates="course_offering", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="course_offering", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    usn = Column(String(50), unique=True, index=True, nullable=False)  # University Seat / Roll Number
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    batch_year = Column(String(20), nullable=True)  # e.g., "2022-2026"
    current_semester = Column(Integer, default=5, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    institution = relationship("Institution", back_populates="students")
    department = relationship("Department", back_populates="students")
    user = relationship("User", back_populates="student", uselist=False)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    marks = relationship("StudentMark", back_populates="student", cascade="all, delete-orphan")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("course_offering_id", "student_id", name="uq_offering_student"),)

    course_offering = relationship("CourseOffering", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")


class CourseOutcome(Base):
    __tablename__ = "course_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False)  # e.g., "CO1", "CO2"
    description = Column(Text, nullable=False)
    blooms_level = Column(String(50), default="Apply", nullable=False)  # Remember, Understand, Apply, Analyze, Evaluate, Create
    target_attainment_percentage = Column(Float, default=70.0, nullable=False)  # e.g., 70%
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (UniqueConstraint("course_id", "code", name="uq_course_co_code"),)

    course = relationship("Course", back_populates="course_outcomes")
    mappings = relationship("CoPoMapping", back_populates="course_outcome", cascade="all, delete-orphan")
    question_mappings = relationship("QuestionCoMapping", back_populates="course_outcome", cascade="all, delete-orphan")
    results = relationship("CoAttainmentResult", back_populates="course_outcome", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="course_outcome", cascade="all, delete-orphan")
    indirect_assessments = relationship("IndirectAssessment", back_populates="course_outcome", cascade="all, delete-orphan")


class ProgramOutcome(Base):
    __tablename__ = "program_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False)  # e.g., "PO1", "PO2" ... "PO12"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("program_id", "code", name="uq_program_po_code"),)

    program = relationship("Program", back_populates="program_outcomes")
    mappings = relationship("CoPoMapping", back_populates="program_outcome", cascade="all, delete-orphan")
    results = relationship("PoAttainmentResult", back_populates="program_outcome", cascade="all, delete-orphan")


class ProgramSpecificOutcome(Base):
    __tablename__ = "program_specific_outcomes"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(20), nullable=False)  # e.g., "PSO1", "PSO2"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("program_id", "code", name="uq_program_pso_code"),)

    program = relationship("Program", back_populates="program_specific_outcomes")
    mappings = relationship("CoPoMapping", back_populates="program_specific_outcome", cascade="all, delete-orphan")
    results = relationship("PoAttainmentResult", back_populates="program_specific_outcome", cascade="all, delete-orphan")


class CoPoMapping(Base):
    __tablename__ = "co_po_mappings"

    id = Column(Integer, primary_key=True, index=True)
    course_outcome_id = Column(Integer, ForeignKey("course_outcomes.id", ondelete="CASCADE"), nullable=False)
    program_outcome_id = Column(Integer, ForeignKey("program_outcomes.id", ondelete="CASCADE"), nullable=True)
    program_specific_outcome_id = Column(Integer, ForeignKey("program_specific_outcomes.id", ondelete="CASCADE"), nullable=True)
    mapping_strength = Column(Integer, default=0, nullable=False)  # 0: None, 1: Low, 2: Medium, 3: High
    justification = Column(Text, nullable=True)

    course_outcome = relationship("CourseOutcome", back_populates="mappings")
    program_outcome = relationship("ProgramOutcome", back_populates="mappings")
    program_specific_outcome = relationship("ProgramSpecificOutcome", back_populates="mappings")
