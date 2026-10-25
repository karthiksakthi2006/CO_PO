from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.models.academic import (
    Institution,
    Department,
    AcademicYear,
    Semester,
    Program,
    Course,
    CourseOffering,
    Student,
    Enrollment,
    CourseOutcome,
    ProgramOutcome,
    ProgramSpecificOutcome,
    CoPoMapping,
)
from backend.app.schemas.academic import (
    InstitutionCreate,
    InstitutionResponse,
    DepartmentCreate,
    DepartmentResponse,
    AcademicYearCreate,
    AcademicYearResponse,
    SemesterCreate,
    SemesterResponse,
    ProgramCreate,
    ProgramResponse,
    CourseCreate,
    CourseResponse,
    CourseOfferingCreate,
    CourseOfferingResponse,
    StudentCreate,
    StudentResponse,
    EnrollmentCreate,
    EnrollmentResponse,
    CourseOutcomeCreate,
    CourseOutcomeResponse,
    ProgramOutcomeCreate,
    ProgramOutcomeResponse,
    ProgramSpecificOutcomeCreate,
    ProgramSpecificOutcomeResponse,
    CoPoMappingBatch,
    CoPoMappingResponse,
)
from backend.app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/academic", tags=["Academic Data Management"])


# --- Institutions ---
@router.get("/institutions", response_model=List[InstitutionResponse])
def get_institutions(db: Session = Depends(get_db)):
    return db.query(Institution).all()


@router.post("/institutions", response_model=InstitutionResponse)
def create_institution(
    inst_in: InstitutionCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN])),
    db: Session = Depends(get_db)
):
    inst = Institution(**inst_in.model_dump())
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# --- Departments ---
@router.get("/departments", response_model=List[DepartmentResponse])
def get_departments(institution_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Department)
    if institution_id:
        query = query.filter(Department.institution_id == institution_id)
    return query.all()


@router.post("/departments", response_model=DepartmentResponse)
def create_department(
    dept_in: DepartmentCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
    db: Session = Depends(get_db)
):
    dept = Department(**dept_in.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


# --- Academic Years & Semesters ---
@router.get("/academic-years", response_model=List[AcademicYearResponse])
def get_academic_years(db: Session = Depends(get_db)):
    return db.query(AcademicYear).order_by(AcademicYear.name.desc()).all()


@router.post("/academic-years", response_model=AcademicYearResponse)
def create_academic_year(
    ay_in: AcademicYearCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN])),
    db: Session = Depends(get_db)
):
    ay = AcademicYear(**ay_in.model_dump())
    db.add(ay)
    db.commit()
    db.refresh(ay)
    return ay


@router.get("/semesters", response_model=List[SemesterResponse])
def get_semesters(academic_year_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Semester)
    if academic_year_id:
        query = query.filter(Semester.academic_year_id == academic_year_id)
    return query.order_by(Semester.semester_number.asc()).all()


@router.post("/semesters", response_model=SemesterResponse)
def create_semester(
    sem_in: SemesterCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD])),
    db: Session = Depends(get_db)
):
    sem = Semester(**sem_in.model_dump())
    db.add(sem)
    db.commit()
    db.refresh(sem)
    return sem


# --- Programs ---
@router.get("/programs", response_model=List[ProgramResponse])
def get_programs(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Program)
    if department_id:
        query = query.filter(Program.department_id == department_id)
    return query.all()


@router.post("/programs", response_model=ProgramResponse)
def create_program(
    prog_in: ProgramCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD])),
    db: Session = Depends(get_db)
):
    prog = Program(**prog_in.model_dump())
    db.add(prog)
    db.commit()
    db.refresh(prog)
    return prog


# --- Courses ---
@router.get("/courses", response_model=List[CourseResponse])
def get_courses(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Course)
    if department_id:
        query = query.filter(Course.department_id == department_id)
    return query.order_by(Course.code.asc()).all()


@router.post("/courses", response_model=CourseResponse)
def create_course(
    course_in: CourseCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    course = Course(**course_in.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


# --- Course Offerings ---
@router.get("/offerings", response_model=List[CourseOfferingResponse])
def get_offerings(
    department_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    faculty_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(CourseOffering).join(Course)
    if department_id:
        query = query.filter(Course.department_id == department_id)
    if semester_id:
        query = query.filter(CourseOffering.semester_id == semester_id)
    if faculty_id:
        query = query.filter(CourseOffering.faculty_id == faculty_id)

    offerings = query.all()
    results = []
    for off in offerings:
        item = CourseOfferingResponse(
            id=off.id,
            course_id=off.course_id,
            academic_year_id=off.academic_year_id,
            semester_id=off.semester_id,
            section=off.section,
            faculty_id=off.faculty_id,
            is_active=off.is_active,
            created_at=off.created_at,
            course_code=off.course.code if off.course else "",
            course_name=off.course.name if off.course else "",
            faculty_name=off.faculty.full_name if off.faculty else "Unassigned",
            semester_name=off.semester.name if off.semester else "",
        )
        results.append(item)
    return results


@router.post("/offerings", response_model=CourseOfferingResponse)
def create_offering(
    off_in: CourseOfferingCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    off = CourseOffering(**off_in.model_dump())
    db.add(off)
    db.commit()
    db.refresh(off)
    return CourseOfferingResponse(
        id=off.id,
        course_id=off.course_id,
        academic_year_id=off.academic_year_id,
        semester_id=off.semester_id,
        section=off.section,
        faculty_id=off.faculty_id,
        is_active=off.is_active,
        created_at=off.created_at,
        course_code=off.course.code if off.course else "",
        course_name=off.course.name if off.course else "",
        faculty_name=off.faculty.full_name if off.faculty else "Unassigned",
        semester_name=off.semester.name if off.semester else "",
    )


# --- Students & Enrollments ---
@router.get("/students", response_model=List[StudentResponse])
def get_students(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Student)
    if department_id:
        query = query.filter(Student.department_id == department_id)
    return query.order_by(Student.usn.asc()).all()


@router.post("/students", response_model=StudentResponse)
def create_student(
    stud_in: StudentCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD])),
    db: Session = Depends(get_db)
):
    stud = Student(**stud_in.model_dump())
    db.add(stud)
    db.commit()
    db.refresh(stud)
    return stud


@router.get("/offerings/{offering_id}/enrollments", response_model=List[EnrollmentResponse])
def get_course_enrollments(offering_id: int, db: Session = Depends(get_db)):
    enrollments = db.query(Enrollment).filter(Enrollment.course_offering_id == offering_id).all()
    results = []
    for enr in enrollments:
        results.append(EnrollmentResponse(
            id=enr.id,
            course_offering_id=enr.course_offering_id,
            student_id=enr.student_id,
            enrolled_at=enr.enrolled_at,
            student_usn=enr.student.usn if enr.student else "",
            student_name=enr.student.full_name if enr.student else "",
        ))
    return results


@router.post("/offerings/{offering_id}/enrollments", response_model=EnrollmentResponse)
@router.post("/offerings/{offering_id}/enroll", response_model=EnrollmentResponse)
def enroll_student(
    offering_id: int,
    enr_in: EnrollmentCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    existing = db.query(Enrollment).filter(
        Enrollment.course_offering_id == offering_id,
        Enrollment.student_id == enr_in.student_id
    ).first()
    if existing:
        return EnrollmentResponse(
            id=existing.id,
            course_offering_id=existing.course_offering_id,
            student_id=existing.student_id,
            enrolled_at=existing.enrolled_at,
            student_usn=existing.student.usn if existing.student else "",
            student_name=existing.student.full_name if existing.student else "",
        )

    enr = Enrollment(course_offering_id=offering_id, student_id=enr_in.student_id)
    db.add(enr)
    db.commit()
    db.refresh(enr)
    return EnrollmentResponse(
        id=enr.id,
        course_offering_id=enr.course_offering_id,
        student_id=enr.student_id,
        enrolled_at=enr.enrolled_at,
        student_usn=enr.student.usn if enr.student else "",
        student_name=enr.student.full_name if enr.student else "",
    )


# --- Course Outcomes (COs) ---
@router.get("/courses/{course_id}/cos", response_model=List[CourseOutcomeResponse])
def get_course_outcomes(course_id: int, db: Session = Depends(get_db)):
    return db.query(CourseOutcome).filter(CourseOutcome.course_id == course_id).order_by(CourseOutcome.code.asc()).all()


@router.post("/courses/{course_id}/cos", response_model=CourseOutcomeResponse)
def create_course_outcome(
    course_id: int,
    co_in: CourseOutcomeCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    co = CourseOutcome(**co_in.model_dump())
    co.course_id = course_id
    db.add(co)
    db.commit()
    db.refresh(co)
    return co


# --- Program Outcomes (POs) & PSOs ---
@router.get("/programs/{program_id}/pos", response_model=List[ProgramOutcomeResponse])
def get_program_outcomes(program_id: int, db: Session = Depends(get_db)):
    return db.query(ProgramOutcome).filter(ProgramOutcome.program_id == program_id).order_by(ProgramOutcome.code.asc()).all()


@router.post("/programs/{program_id}/pos", response_model=ProgramOutcomeResponse)
def create_program_outcome(
    program_id: int,
    po_in: ProgramOutcomeCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD])),
    db: Session = Depends(get_db)
):
    po = ProgramOutcome(**po_in.model_dump())
    po.program_id = program_id
    db.add(po)
    db.commit()
    db.refresh(po)
    return po


@router.get("/programs/{program_id}/psos", response_model=List[ProgramSpecificOutcomeResponse])
def get_program_psos(program_id: int, db: Session = Depends(get_db)):
    return db.query(ProgramSpecificOutcome).filter(ProgramSpecificOutcome.program_id == program_id).order_by(ProgramSpecificOutcome.code.asc()).all()


# --- CO-PO/PSO Mapping Matrix ---
@router.get("/courses/{course_id}/mappings")
def get_co_po_matrix(course_id: int, db: Session = Depends(get_db)):
    """
    Returns the complete CO-PO and CO-PSO mapping matrix with statistics.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    cos = db.query(CourseOutcome).filter(CourseOutcome.course_id == course_id).order_by(CourseOutcome.code.asc()).all()
    pos = db.query(ProgramOutcome).filter(ProgramOutcome.program_id == course.program_id).order_by(ProgramOutcome.code.asc()).all() if course.program_id else []
    psos = db.query(ProgramSpecificOutcome).filter(ProgramSpecificOutcome.program_id == course.program_id).order_by(ProgramSpecificOutcome.code.asc()).all() if course.program_id else []

    co_ids = [c.id for c in cos]
    existing_mappings = db.query(CoPoMapping).filter(CoPoMapping.course_outcome_id.in_(co_ids)).all() if co_ids else []

    # Build matrix map: (co_id, po_id or pso_id) -> mapping_strength
    matrix = {}
    for m in existing_mappings:
        key = f"CO_{m.course_outcome_id}_PO_{m.program_outcome_id}" if m.program_outcome_id else f"CO_{m.course_outcome_id}_PSO_{m.program_specific_outcome_id}"
        matrix[key] = {
            "id": m.id,
            "strength": m.mapping_strength,
            "justification": m.justification,
        }

    # Coverage statistics
    total_cells = len(cos) * (len(pos) + len(psos))
    mapped_cells = sum(1 for m in existing_mappings if m.mapping_strength > 0)
    coverage_pct = round((mapped_cells / total_cells * 100.0), 1) if total_cells > 0 else 0.0

    return {
        "course": {"id": course.id, "code": course.code, "name": course.name},
        "cos": [{"id": c.id, "code": c.code, "description": c.description, "blooms_level": c.blooms_level} for c in cos],
        "pos": [{"id": p.id, "code": p.code, "title": p.title} for p in pos],
        "psos": [{"id": ps.id, "code": ps.code, "title": ps.title} for ps in psos],
        "matrix": matrix,
        "stats": {
            "total_cells": total_cells,
            "mapped_cells": mapped_cells,
            "coverage_percentage": coverage_pct,
        }
    }


@router.post("/courses/{course_id}/mappings/batch")
def batch_update_mappings(
    course_id: int,
    batch_data: CoPoMappingBatch,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Saves or updates CO-PO/PSO mapping strengths in batch."""
    for entry in batch_data.mappings:
        existing = db.query(CoPoMapping).filter(
            CoPoMapping.course_outcome_id == entry.course_outcome_id,
            CoPoMapping.program_outcome_id == entry.program_outcome_id,
            CoPoMapping.program_specific_outcome_id == entry.program_specific_outcome_id
        ).first()

        if existing:
            existing.mapping_strength = entry.mapping_strength
            existing.justification = entry.justification
        else:
            new_m = CoPoMapping(
                course_outcome_id=entry.course_outcome_id,
                program_outcome_id=entry.program_outcome_id,
                program_specific_outcome_id=entry.program_specific_outcome_id,
                mapping_strength=entry.mapping_strength,
                justification=entry.justification,
            )
            db.add(new_m)

    db.commit()
    return {"message": "Mapping matrix updated successfully"}


# --- Student Performance History (Authorized) ---
@router.get("/students/{student_id}/performance")
def get_student_performance(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves authorized academic history, assessment marks, and CO performance for a student.
    Enforces student privacy boundary: Students can ONLY access their own records.
    """
    if current_user.role == UserRole.STUDENT and current_user.student_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Students are strictly restricted to their own academic performance records.",
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Get enrollments
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    
    courses_performance = []
    for enr in enrollments:
        offering = enr.course_offering
        if not offering:
            continue

        # Get marks for this offering
        from backend.app.models.assessment import StudentMark, Question, Assessment
        marks = db.query(StudentMark).join(Question).join(Assessment).filter(
            Assessment.course_offering_id == offering.id,
            StudentMark.student_id == student_id
        ).all()

        marks_list = []
        total_obtained = 0.0
        total_max = 0.0

        for m in marks:
            q = m.question
            ass = q.assessment if q else None
            is_abs = m.is_absent
            score = m.marks_obtained if not is_abs else 0.0
            max_m = q.max_marks if q else 0.0

            if not is_abs and m.marks_obtained is not None:
                total_obtained += score
                total_max += max_m

            marks_list.append({
                "assessment_name": ass.name if ass else "",
                "question_number": q.question_number if q else "",
                "max_marks": max_m,
                "marks_obtained": m.marks_obtained,
                "is_absent": is_abs,
            })

        course_pct = round((total_obtained / total_max * 100.0), 1) if total_max > 0 else 0.0

        courses_performance.append({
            "offering_id": offering.id,
            "course_code": offering.course.code if offering.course else "",
            "course_name": offering.course.name if offering.course else "",
            "section": offering.section,
            "overall_score_percentage": course_pct,
            "marks_breakdown": marks_list,
        })

    return {
        "student": {
            "id": student.id,
            "usn": student.usn,
            "full_name": student.full_name,
            "email": student.email,
            "batch_year": student.batch_year,
            "current_semester": student.current_semester,
        },
        "courses_performance": courses_performance,
    }
