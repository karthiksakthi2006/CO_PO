from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.attainment import AttainmentSeverity
from backend.app.models.intervention import InterventionStatus, EffectivenessRating


class InterventionCreate(BaseModel):
    course_offering_id: int
    course_outcome_id: int
    gap_percentage_points: float
    severity: AttainmentSeverity = AttainmentSeverity.MODERATE
    root_cause_analysis: str
    action_plan: str
    pedagogical_tool: str = "Remedial Problem-Solving Tutorials"
    assigned_faculty_id: Optional[int] = None
    target_completion_date: Optional[datetime] = None
    pre_intervention_attainment: float


class InterventionUpdate(BaseModel):
    status: Optional[InterventionStatus] = None
    action_plan: Optional[str] = None
    post_intervention_attainment: Optional[float] = None
    effectiveness_rating: Optional[EffectivenessRating] = None


class ReassessmentCreate(BaseModel):
    intervention_id: int
    assessment_name: str
    conduct_date: Optional[datetime] = None
    total_students: int
    students_passed: int
    average_score: float
    reassessment_attainment: float
    notes: Optional[str] = None


class ReassessmentResponse(ReassessmentCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class InterventionResponse(BaseModel):
    id: int
    course_offering_id: int
    course_outcome_id: int
    co_code: Optional[str] = None
    gap_percentage_points: float
    severity: AttainmentSeverity
    root_cause_analysis: str
    action_plan: str
    pedagogical_tool: str
    assigned_faculty_id: Optional[int] = None
    assigned_faculty_name: Optional[str] = None
    target_completion_date: Optional[datetime] = None
    status: InterventionStatus
    pre_intervention_attainment: float
    post_intervention_attainment: Optional[float] = None
    improvement_percentage_points: Optional[float] = None
    effectiveness_rating: EffectivenessRating
    created_at: datetime
    updated_at: datetime
    reassessments: List[ReassessmentResponse] = []

    model_config = ConfigDict(from_attributes=True)
