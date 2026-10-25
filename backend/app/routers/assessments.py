from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.models.academic import CourseOffering, Student, Enrollment, CourseOutcome
from backend.app.models.assessment import (
    Assessment,
    Question,
    QuestionCoMapping,
    StudentMark,
    IndirectAssessment,
)
from backend.app.models.audit import ImportJob
from backend.app.schemas.assessment import (
    AssessmentCreate,
    AssessmentResponse,
    QuestionCreate,
    QuestionResponse,
    StudentMarkBatch,
    StudentMarkResponse,
    IndirectAssessmentCreate,
    IndirectAssessmentResponse,
)
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.services.import_service import (
    preview_spreadsheet,
    validate_student_roster,
    validate_assessment_marks,
    generate_student_roster_template,
    generate_marks_import_template,
    parse_spreadsheet_file,
)

router = APIRouter(prefix="/assessments", tags=["Assessment & Marks Management"])


# --- Assessments ---
@router.get("/offerings/{offering_id}", response_model=List[AssessmentResponse])
def get_assessments(offering_id: int, db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.course_offering_id == offering_id).all()
    results = []
    for a in assessments:
        results.append(AssessmentResponse(
            id=a.id,
            course_offering_id=a.course_offering_id,
            name=a.name,
            assessment_type=a.assessment_type,
            weight_percentage=a.weight_percentage,
            max_marks=a.max_marks,
            conduct_date=a.conduct_date,
            created_at=a.created_at,
            question_count=len(a.questions),
        ))
    return results


@router.post("/offerings/{offering_id}", response_model=AssessmentResponse)
def create_assessment(
    offering_id: int,
    ass_in: AssessmentCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    ass = Assessment(**ass_in.model_dump())
    ass.course_offering_id = offering_id
    db.add(ass)
    db.commit()
    db.refresh(ass)
    return AssessmentResponse(
        id=ass.id,
        course_offering_id=ass.course_offering_id,
        name=ass.name,
        assessment_type=ass.assessment_type,
        weight_percentage=ass.weight_percentage,
        max_marks=ass.max_marks,
        conduct_date=ass.conduct_date,
        created_at=ass.created_at,
        question_count=0,
    )


# --- Questions ---
@router.get("/{assessment_id}/questions", response_model=List[QuestionResponse])
def get_questions(assessment_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    results = []
    for q in questions:
        mapped_codes = [m.course_outcome.code for m in q.co_mappings if m.course_outcome]
        results.append(QuestionResponse(
            id=q.id,
            assessment_id=q.assessment_id,
            question_number=q.question_number,
            max_marks=q.max_marks,
            description=q.description,
            mapped_co_codes=mapped_codes,
        ))
    return results


@router.post("/{assessment_id}/questions", response_model=QuestionResponse)
def create_question(
    assessment_id: int,
    q_in: QuestionCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    q = Question(
        assessment_id=assessment_id,
        question_number=q_in.question_number,
        max_marks=q_in.max_marks,
        description=q_in.description,
    )
    db.add(q)
    db.flush()

    mapped_codes = []
    if q_in.course_outcome_ids:
        for co_id in q_in.course_outcome_ids:
            mapping = QuestionCoMapping(
                question_id=q.id,
                course_outcome_id=co_id,
                weight=1.0,
            )
            db.add(mapping)
            co = db.query(CourseOutcome).filter(CourseOutcome.id == co_id).first()
            if co:
                mapped_codes.append(co.code)

    db.commit()
    db.refresh(q)
    return QuestionResponse(
        id=q.id,
        assessment_id=q.assessment_id,
        question_number=q.question_number,
        max_marks=q.max_marks,
        description=q.description,
        mapped_co_codes=mapped_codes,
    )


# --- Marks ---
@router.get("/{assessment_id}/marks", response_model=List[StudentMarkResponse])
def get_assessment_marks(assessment_id: int, db: Session = Depends(get_db)):
    marks = db.query(StudentMark).filter(StudentMark.assessment_id == assessment_id).all()
    results = []
    for m in marks:
        results.append(StudentMarkResponse(
            id=m.id,
            assessment_id=m.assessment_id,
            question_id=m.question_id,
            student_id=m.student_id,
            marks_obtained=m.marks_obtained,
            is_absent=m.is_absent,
            remarks=m.remarks,
            student_usn=m.student.usn if m.student else "",
            student_name=m.student.full_name if m.student else "",
        ))
    return results


@router.post("/{assessment_id}/marks/batch")
def save_marks_batch(
    assessment_id: int,
    batch_data: StudentMarkBatch,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    for entry in batch_data.marks:
        existing = db.query(StudentMark).filter(
            StudentMark.question_id == entry.question_id,
            StudentMark.student_id == entry.student_id
        ).first()

        if existing:
            existing.marks_obtained = entry.marks_obtained
            existing.is_absent = entry.is_absent
            existing.remarks = entry.remarks
        else:
            new_mark = StudentMark(
                assessment_id=assessment_id,
                question_id=entry.question_id,
                student_id=entry.student_id,
                marks_obtained=entry.marks_obtained,
                is_absent=entry.is_absent,
                remarks=entry.remarks,
            )
            db.add(new_mark)

    db.commit()
    return {"message": "Marks saved successfully", "count": len(batch_data.marks)}


# --- Template Downloads ---
@router.get("/templates/student-roster")
def download_student_template():
    csv_bytes = generate_student_roster_template()
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_roster_template.csv"}
    )


@router.get("/templates/assessment-marks/{assessment_id}")
def download_marks_template(assessment_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    q_data = [{"question_number": q.question_number, "max_marks": q.max_marks} for q in questions]
    csv_bytes = generate_marks_import_template(q_data)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=marks_template_assessment_{assessment_id}.csv"}
    )


# --- File Upload Preview & Validation ---
@router.post("/import/preview")
async def preview_upload_file(file: UploadFile = File(...)):
    """Previews spreadsheet columns and sample rows."""
    file_bytes = await file.read()
    try:
        preview = preview_spreadsheet(file_bytes, file.filename)
        return preview
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import/validate-marks")
async def validate_marks_file(
    assessment_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Validates uploaded marks spreadsheet against questions and enrolled roster."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Assessment has no questions configured.")

    enrollments = db.query(Enrollment).filter(Enrollment.course_offering_id == assessment.course_offering_id).all()
    enrolled_usns = [e.student.usn for e in enrollments if e.student]

    file_bytes = await file.read()
    try:
        df = parse_spreadsheet_file(file_bytes, file.filename)
        q_dicts = [{"id": q.id, "question_number": q.question_number, "max_marks": q.max_marks} for q in questions]
        valid_marks, error_rows = validate_assessment_marks(df, q_dicts, enrolled_usns)

        return {
            "total_rows": len(df),
            "valid_records_count": len(valid_marks),
            "error_records_count": len(error_rows),
            "errors": error_rows,
            "can_commit": len(error_rows) == 0,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import/commit-marks")
async def commit_marks_file(
    assessment_id: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Transactionally commits valid spreadsheet marks to database."""
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    enrollments = db.query(Enrollment).filter(Enrollment.course_offering_id == assessment.course_offering_id).all()
    usn_to_student_id = {e.student.usn: e.student_id for e in enrollments if e.student}

    file_bytes = await file.read()
    df = parse_spreadsheet_file(file_bytes, file.filename)
    q_dicts = [{"id": q.id, "question_number": q.question_number, "max_marks": q.max_marks} for q in questions]
    valid_marks, error_rows = validate_assessment_marks(df, q_dicts, list(usn_to_student_id.keys()))

    if error_rows:
        raise HTTPException(status_code=400, detail="Cannot commit: validation errors exist in spreadsheet.")

    # Save marks transactionally
    imported_count = 0
    for item in valid_marks:
        student_id = usn_to_student_id.get(item["usn"])
        if not student_id:
            continue

        existing = db.query(StudentMark).filter(
            StudentMark.question_id == item["question_id"],
            StudentMark.student_id == student_id
        ).first()

        if existing:
            existing.marks_obtained = item["marks_obtained"]
            existing.is_absent = item["is_absent"]
        else:
            new_mark = StudentMark(
                assessment_id=assessment_id,
                question_id=item["question_id"],
                student_id=student_id,
                marks_obtained=item["marks_obtained"],
                is_absent=item["is_absent"],
            )
            db.add(new_mark)
        imported_count += 1

    # Record import job in audit log
    job = ImportJob(
        user_id=current_user.id,
        import_type="ASSESSMENT_MARKS",
        file_name=file.filename,
        status="SUCCESS",
        total_rows=len(df),
        imported_rows=imported_count,
        failed_rows=0,
    )
    db.add(job)
    db.commit()

    return {
        "message": "Marks committed successfully",
        "imported_count": imported_count,
        "total_rows": len(df),
    }
