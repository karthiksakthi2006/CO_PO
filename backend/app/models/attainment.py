import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from backend.app.database import Base


class DirectAttainmentMethod(str, enum.Enum):
    THRESHOLD = "THRESHOLD"      # Method A: % students scoring >= threshold% of max marks
    NORMALIZED = "NORMALIZED"    # Method B: sum(student marks) / sum(max marks)


class MissingMarkPolicy(str, enum.Enum):
    EXCLUDE = "EXCLUDE"          # Exclude absent/missing students from denominator
    ZERO = "ZERO"                # Count absent/missing as 0 marks, include in denominator


class AttainmentSeverity(str, enum.Enum):
    ON_TARGET = "ON_TARGET"      # Gap <= 0 (target met or exceeded)
    MODERATE = "MODERATE"        # 0 < Gap < 10 percentage points below target
    HIGH = "HIGH"                # 10 <= Gap < 20 percentage points below target
    CRITICAL = "CRITICAL"        # Gap >= 20 percentage points below target


class AttainmentConfiguration(Base):
    __tablename__ = "attainment_configurations"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False)
    
    direct_method = Column(Enum(DirectAttainmentMethod), default=DirectAttainmentMethod.THRESHOLD, nullable=False)
    threshold_percentage = Column(Float, default=60.0, nullable=False)  # student score threshold (e.g. 60% of question max marks)
    target_percentage = Column(Float, default=70.0, nullable=False)     # target attainment (e.g. 70% of students meeting threshold)
    
    # Attainment Levels
    level1_threshold = Column(Float, default=60.0, nullable=False)     # < 60% -> Level 1
    level2_threshold = Column(Float, default=70.0, nullable=False)     # 60% - 70% -> Level 2, >= 70% -> Level 3
    level3_threshold = Column(Float, default=80.0, nullable=False)
    
    # Direct vs Indirect Weighting
    enable_indirect = Column(Integer, default=1, nullable=False)       # 1=True, 0=False
    direct_weight = Column(Float, default=80.0, nullable=False)         # 80%
    indirect_weight = Column(Float, default=20.0, nullable=False)       # 20%
    
    missing_mark_policy = Column(Enum(MissingMarkPolicy), default=MissingMarkPolicy.EXCLUDE, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    course_offering = relationship("CourseOffering", back_populates="attainment_configurations")
    attainment_runs = relationship("AttainmentRun", back_populates="configuration")


class AttainmentRun(Base):
    __tablename__ = "attainment_runs"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False)
    configuration_id = Column(Integer, ForeignKey("attainment_configurations.id", ondelete="SET NULL"), nullable=True)
    run_timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    method_used = Column(String(50), nullable=False)
    status = Column(String(50), default="COMPLETED", nullable=False)
    summary_notes = Column(Text, nullable=True)
    run_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    course_offering = relationship("CourseOffering", back_populates="attainment_runs")
    configuration = relationship("AttainmentConfiguration", back_populates="attainment_runs")
    run_by_user = relationship("User", foreign_keys=[run_by_user_id])
    co_results = relationship("CoAttainmentResult", back_populates="attainment_run", cascade="all, delete-orphan")
    po_results = relationship("PoAttainmentResult", back_populates="attainment_run", cascade="all, delete-orphan")


class CoAttainmentResult(Base):
    __tablename__ = "co_attainment_results"

    id = Column(Integer, primary_key=True, index=True)
    attainment_run_id = Column(Integer, ForeignKey("attainment_runs.id", ondelete="CASCADE"), nullable=False)
    course_outcome_id = Column(Integer, ForeignKey("course_outcomes.id", ondelete="CASCADE"), nullable=False)
    
    direct_attainment = Column(Float, nullable=False)
    indirect_attainment = Column(Float, nullable=True)
    overall_attainment = Column(Float, nullable=False)
    target_attainment = Column(Float, nullable=False)
    attainment_level = Column(Integer, default=1, nullable=False)  # 1, 2, or 3
    
    gap_percentage_points = Column(Float, nullable=False)  # target - actual (positive = below target)
    severity = Column(Enum(AttainmentSeverity), default=AttainmentSeverity.ON_TARGET, nullable=False)
    eligible_students_count = Column(Integer, default=0, nullable=False)
    details_json = Column(Text, nullable=True)  # breakdown of question/component contributions

    attainment_run = relationship("AttainmentRun", back_populates="co_results")
    course_outcome = relationship("CourseOutcome", back_populates="results")


class PoAttainmentResult(Base):
    __tablename__ = "po_attainment_results"

    id = Column(Integer, primary_key=True, index=True)
    attainment_run_id = Column(Integer, ForeignKey("attainment_runs.id", ondelete="CASCADE"), nullable=False)
    program_outcome_id = Column(Integer, ForeignKey("program_outcomes.id", ondelete="CASCADE"), nullable=True)
    program_specific_outcome_id = Column(Integer, ForeignKey("program_specific_outcomes.id", ondelete="CASCADE"), nullable=True)
    outcome_code = Column(String(20), nullable=False)  # e.g., "PO1", "PSO1"
    
    calculated_attainment = Column(Float, nullable=False)
    average_strength = Column(Float, default=0.0, nullable=False)
    mapped_co_count = Column(Integer, default=0, nullable=False)

    attainment_run = relationship("AttainmentRun", back_populates="po_results")
    program_outcome = relationship("ProgramOutcome", back_populates="results")
    program_specific_outcome = relationship("ProgramSpecificOutcome", back_populates="results")
