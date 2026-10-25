from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class InstitutionCreate(BaseModel):
    code: str
    name: str
    address: Optional[str] = None
    contact_email: Optional[str] = None


class InstitutionResponse(InstitutionCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(BaseModel):
    institution_id: int
    code: str
    name: str
    head_name: Optional[str] = None


class DepartmentResponse(DepartmentCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AcademicYearCreate(BaseModel):
    name: str
    is_current: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AcademicYearResponse(AcademicYearCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SemesterCreate(BaseModel):
    academic_year_id: int
    name: str
    semester_number: int
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SemesterResponse(SemesterCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProgramCreate(BaseModel):
    department_id: int
    code: str
    name: str
    degree: str = "B.Tech"
    total_credits: int = 160


class ProgramResponse(ProgramCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    department_id: int
    program_id: Optional[int] = None
    code: str
    name: str
    credits: int = 4
    semester_number: int = 5
    description: Optional[str] = None


class CourseResponse(CourseCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseOfferingCreate(BaseModel):
    course_id: int
    academic_year_id: int
    semester_id: int
    section: str = "A"
    faculty_id: Optional[int] = None
    is_active: bool = True


class CourseOfferingResponse(CourseOfferingCreate):
    id: int
    created_at: datetime
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    faculty_name: Optional[str] = None
    semester_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StudentCreate(BaseModel):
    institution_id: int
    department_id: int
    usn: str
    full_name: str
    email: Optional[str] = None
    batch_year: Optional[str] = "2022-2026"
    current_semester: int = 5


class StudentResponse(StudentCreate):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnrollmentCreate(BaseModel):
    course_offering_id: int
    student_id: int


class EnrollmentResponse(EnrollmentCreate):
    id: int
    enrolled_at: datetime
    student_usn: Optional[str] = None
    student_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CourseOutcomeCreate(BaseModel):
    course_id: int
    code: str
    description: str
    blooms_level: str = "Apply"
    target_attainment_percentage: float = 70.0


class CourseOutcomeResponse(CourseOutcomeCreate):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProgramOutcomeCreate(BaseModel):
    program_id: int
    code: str
    title: str
    description: str


class ProgramOutcomeResponse(ProgramOutcomeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProgramSpecificOutcomeCreate(BaseModel):
    program_id: int
    code: str
    title: str
    description: str


class ProgramSpecificOutcomeResponse(ProgramSpecificOutcomeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CoPoMappingEntry(BaseModel):
    course_outcome_id: int
    program_outcome_id: Optional[int] = None
    program_specific_outcome_id: Optional[int] = None
    mapping_strength: int = 0  # 0, 1, 2, 3
    justification: Optional[str] = None


class CoPoMappingBatch(BaseModel):
    mappings: List[CoPoMappingEntry]


class CoPoMappingResponse(CoPoMappingEntry):
    id: int

    model_config = ConfigDict(from_attributes=True)
