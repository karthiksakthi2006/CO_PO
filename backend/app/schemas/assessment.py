from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.assessment import AssessmentType


class AssessmentCreate(BaseModel):
    course_offering_id: int
    name: str
    assessment_type: AssessmentType = AssessmentType.CIE
    weight_percentage: float = 50.0
    max_marks: float = 50.0
    conduct_date: Optional[datetime] = None


class AssessmentResponse(AssessmentCreate):
    id: int
    created_at: datetime
    question_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)


class QuestionCreate(BaseModel):
    assessment_id: int
    question_number: str
    max_marks: float
    description: Optional[str] = None
    course_outcome_ids: Optional[List[int]] = None  # optional mapping at creation


class QuestionResponse(BaseModel):
    id: int
    assessment_id: int
    question_number: str
    max_marks: float
    description: Optional[str] = None
    mapped_co_codes: Optional[List[str]] = []

    model_config = ConfigDict(from_attributes=True)


class QuestionCoMappingCreate(BaseModel):
    question_id: int
    course_outcome_id: int
    marks_allocated: Optional[float] = None
    weight: float = 1.0


class QuestionCoMappingResponse(QuestionCoMappingCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudentMarkCreate(BaseModel):
    assessment_id: int
    question_id: int
    student_id: int
    marks_obtained: Optional[float] = None
    is_absent: bool = False
    remarks: Optional[str] = None


class StudentMarkBatch(BaseModel):
    marks: List[StudentMarkCreate]


class StudentMarkResponse(StudentMarkCreate):
    id: int
    student_usn: Optional[str] = None
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class IndirectAssessmentCreate(BaseModel):
    course_offering_id: int
    course_outcome_id: int
    survey_name: str = "Course Exit Survey"
    total_responses: int = 0
    average_score: float = 0.0
    max_possible_score: float = 5.0
    attainment_percentage: float = 0.0


class IndirectAssessmentResponse(IndirectAssessmentCreate):
    id: int
    conduct_date: datetime

    model_config = ConfigDict(from_attributes=True)
