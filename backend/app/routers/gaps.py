from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.academic import CourseOffering, CourseOutcome, Enrollment, Student
from backend.app.models.assessment import Assessment, Question, QuestionCoMapping, StudentMark
from backend.app.models.attainment import AttainmentRun, CoAttainmentResult
from backend.app.analytics.gap_detector import (
    analyze_co_gaps,
    detect_weak_questions,
    detect_component_disparities,
    identify_at_risk_students,
)

router = APIRouter(prefix="/gaps", tags=["Gap Detection & Academic Insights"])


@router.get("/offerings/{offering_id}/analysis")
def get_comprehensive_gap_analysis(offering_id: int, db: Session = Depends(get_db)):
    """
    Runs multi-dimensional gap detection on course offering:
    1. Underperforming COs with cognitive taxonomy analysis
    2. Weak questions with student success rates
    3. Evaluation component disparities (CIE vs SEE)
    4. At-risk students with rule-based criteria
    """
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    # Get latest attainment run
    latest_run = db.query(AttainmentRun).filter(
        AttainmentRun.course_offering_id == offering_id
    ).order_by(AttainmentRun.id.desc()).first()

    if not latest_run:
        return {
            "has_data": False,
            "message": "No attainment calculation runs found for this course offering. Run calculation first.",
            "co_gaps": [],
            "weak_questions": [],
            "component_disparities": [],
            "at_risk_students": [],
        }

    # 1. Analyze CO Gaps
    co_data = []
    for cr in latest_run.co_results:
        co_data.append({
            "co_code": cr.course_outcome.code if cr.course_outcome else "",
            "co_description": cr.course_outcome.description if cr.course_outcome else "",
            "blooms_level": cr.course_outcome.blooms_level if cr.course_outcome else "Apply",
            "target_attainment": cr.target_attainment,
            "actual_attainment": cr.overall_attainment,
            "gap_percentage_points": cr.gap_percentage_points,
            "severity": cr.severity.value,
        })
    co_gaps = analyze_co_gaps(co_data)

    # 2. Analyze Question Stats
    assessments = db.query(Assessment).filter(Assessment.course_offering_id == offering.id).all()
    q_stats = []
    component_scores = {}

    for ass in assessments:
        total_ass_marks = 0.0
        total_ass_max = 0.0

        for q in ass.questions:
            marks = db.query(StudentMark).filter(StudentMark.question_id == q.id).all()
            valid_marks = [m.marks_obtained for m in marks if not m.is_absent and m.marks_obtained is not None]
            
            att_pct = 0.0
            if valid_marks and q.max_marks > 0:
                pass_count = sum(1 for m in valid_marks if m >= 0.6 * q.max_marks)
                att_pct = (pass_count / len(valid_marks)) * 100.0

            mapped_co = q.co_mappings[0].course_outcome.code if q.co_mappings and q.co_mappings[0].course_outcome else ""
            q_stats.append({
                "question_number": f"{ass.name} - {q.question_number}",
                "max_marks": q.max_marks,
                "attainment_percentage": round(att_pct, 1),
                "mapped_co_code": mapped_co,
            })

            total_ass_marks += sum(valid_marks)
            total_ass_max += q.max_marks * len(valid_marks)

        if total_ass_max > 0:
            component_type = ass.assessment_type.value
            component_scores[component_type] = round((total_ass_marks / total_ass_max) * 100.0, 1)

    weak_questions = detect_weak_questions(q_stats, weakness_threshold_pct=50.0)

    # 3. Component disparities
    component_disparities = detect_component_disparities(component_scores, disparity_threshold=15.0)

    # 4. At-risk students
    enrollments = db.query(Enrollment).filter(Enrollment.course_offering_id == offering_id).all()
    student_records = []

    for enr in enrollments:
        stud = enr.student
        if not stud:
            continue

        stud_marks = db.query(StudentMark).join(Question).join(Assessment).filter(
            Assessment.course_offering_id == offering_id,
            StudentMark.student_id == stud.id
        ).all()

        total_obtained = sum(m.marks_obtained for m in stud_marks if not m.is_absent and m.marks_obtained is not None)
        total_possible = sum(m.question.max_marks for m in stud_marks if not m.is_absent and m.marks_obtained is not None)
        
        avg_pct = (total_obtained / total_possible * 100.0) if total_possible > 0 else 0.0

        # Check which COs student scored low on
        failed_cos = []
        for cr in latest_run.co_results:
            if cr.course_outcome:
                # If student's overall score is below target, mark for review
                if avg_pct < cr.target_attainment - 15.0:
                    failed_cos.append(cr.course_outcome.code)

        student_records.append({
            "student_id": stud.id,
            "usn": stud.usn,
            "full_name": stud.full_name,
            "average_score_pct": round(avg_pct, 1),
            "failed_cos": list(set(failed_cos)),
        })

    at_risk_students = identify_at_risk_students(student_records, failing_co_threshold=2)

    return {
        "has_data": True,
        "run_id": latest_run.id,
        "co_gaps": co_gaps,
        "weak_questions": weak_questions,
        "component_disparities": component_disparities,
        "at_risk_students": at_risk_students,
        "summary": {
            "total_cos": len(co_data),
            "underperforming_cos_count": len(co_gaps),
            "weak_questions_count": len(weak_questions),
            "at_risk_students_count": len(at_risk_students),
        }
    }
