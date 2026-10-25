import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.attainment import AttainmentSeverity


class InterventionStatus(str, enum.Enum):
    IDENTIFIED = "IDENTIFIED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class EffectivenessRating(str, enum.Enum):
    PENDING_REASSESSMENT = "PENDING_REASSESSMENT"
    EFFECTIVE = "EFFECTIVE"
    PARTIALLY_EFFECTIVE = "PARTIALLY_EFFECTIVE"
    NEEDS_FURTHER_ACTION = "NEEDS_FURTHER_ACTION"


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False)
    course_outcome_id = Column(Integer, ForeignKey("course_outcomes.id", ondelete="CASCADE"), nullable=False)
    
    gap_percentage_points = Column(Float, nullable=False)
    severity = Column(Enum(AttainmentSeverity), default=AttainmentSeverity.MODERATE, nullable=False)
    
    root_cause_analysis = Column(Text, nullable=False)
    action_plan = Column(Text, nullable=False)
    pedagogical_tool = Column(String(255), default="Remedial Sessions & Guided Problem Sets", nullable=False)
    
    assigned_faculty_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    target_completion_date = Column(DateTime, nullable=True)
    status = Column(Enum(InterventionStatus), default=InterventionStatus.IDENTIFIED, nullable=False)
    
    pre_intervention_attainment = Column(Float, nullable=False)
    post_intervention_attainment = Column(Float, nullable=True)
    improvement_percentage_points = Column(Float, nullable=True)
    effectiveness_rating = Column(Enum(EffectivenessRating), default=EffectivenessRating.PENDING_REASSESSMENT, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    course_offering = relationship("CourseOffering", back_populates="interventions")
    course_outcome = relationship("CourseOutcome", back_populates="interventions")
    assigned_faculty = relationship("User", foreign_keys=[assigned_faculty_id])
    reassessments = relationship("Reassessment", back_populates="intervention", cascade="all, delete-orphan")


class Reassessment(Base):
    __tablename__ = "reassessments"

    id = Column(Integer, primary_key=True, index=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id", ondelete="CASCADE"), nullable=False)
    assessment_name = Column(String(255), nullable=False)  # e.g., "Remedial Quiz 1", "Re-examination Test"
    conduct_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    total_students = Column(Integer, default=0, nullable=False)
    students_passed = Column(Integer, default=0, nullable=False)
    average_score = Column(Float, default=0.0, nullable=False)
    reassessment_attainment = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    intervention = relationship("Intervention", back_populates="reassessments")
