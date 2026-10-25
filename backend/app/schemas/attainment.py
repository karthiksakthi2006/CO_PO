from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.attainment import DirectAttainmentMethod, MissingMarkPolicy, AttainmentSeverity


class AttainmentConfigCreate(BaseModel):
    course_offering_id: int
    direct_method: DirectAttainmentMethod = DirectAttainmentMethod.THRESHOLD
    threshold_percentage: float = 60.0
    target_percentage: float = 70.0
    level1_threshold: float = 60.0
    level2_threshold: float = 70.0
    level3_threshold: float = 80.0
    enable_indirect: int = 1
    direct_weight: float = 80.0
    indirect_weight: float = 20.0
    missing_mark_policy: MissingMarkPolicy = MissingMarkPolicy.EXCLUDE


class AttainmentConfigResponse(AttainmentConfigCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttainmentRunRequest(BaseModel):
    course_offering_id: int
    configuration_id: Optional[int] = None
    summary_notes: Optional[str] = None


class CoAttainmentResultResponse(BaseModel):
    id: int
    course_outcome_id: int
    co_code: Optional[str] = None
    co_description: Optional[str] = None
    blooms_level: Optional[str] = None
    direct_attainment: float
    indirect_attainment: Optional[float] = None
    overall_attainment: float
    target_attainment: float
    attainment_level: int
    gap_percentage_points: float
    severity: AttainmentSeverity
    eligible_students_count: int
    details_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PoAttainmentResultResponse(BaseModel):
    id: int
    outcome_code: str
    calculated_attainment: float
    average_strength: float
    mapped_co_count: int

    model_config = ConfigDict(from_attributes=True)


class AttainmentRunResponse(BaseModel):
    id: int
    course_offering_id: int
    configuration_id: Optional[int] = None
    run_timestamp: datetime
    method_used: str
    status: str
    summary_notes: Optional[str] = None
    co_results: List[CoAttainmentResultResponse] = []
    po_results: List[PoAttainmentResultResponse] = []

    model_config = ConfigDict(from_attributes=True)
