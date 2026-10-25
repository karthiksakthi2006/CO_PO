from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.academic import Course, CourseOffering, Student, Enrollment, CourseOutcome, Semester
from backend.app.models.attainment import AttainmentRun, CoAttainmentResult, AttainmentSeverity
from backend.app.models.intervention import Intervention, InterventionStatus

router = APIRouter(prefix="/dashboard", tags=["Analytics Dashboard"])


@router.get("/metrics")
def get_dashboard_metrics(
    department_id: Optional[int] = None,
    semester_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Computes real, database-backed KPIs across institutions, courses, and student cohorts.
    No hardcoded values.
    """
    # Active courses query
    course_q = db.query(Course)
    if department_id:
        course_q = course_q.filter(Course.department_id == department_id)
    total_courses = course_q.count()

    # Total enrolled students query
    student_q = db.query(Student)
    if department_id:
        student_q = student_q.filter(Student.department_id == department_id)
    total_students = student_q.count()

    # Attainment results query (get latest run for each offering)
    offering_q = db.query(CourseOffering)
    if course_id:
        offering_q = offering_q.filter(CourseOffering.course_id == course_id)
    if semester_id:
        offering_q = offering_q.filter(CourseOffering.semester_id == semester_id)

    offerings = offering_q.all()
    offering_ids = [o.id for o in offerings]

    total_cos_evaluated = 0
    cos_meeting_target = 0
    cos_below_target = 0
    total_attainment_sum = 0.0

    severity_counts = {
        "ON_TARGET": 0,
        "MODERATE": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    co_bar_data = []

    for off in offerings:
        latest_run = db.query(AttainmentRun).filter(
            AttainmentRun.course_offering_id == off.id
        ).order_by(AttainmentRun.id.desc()).first()

        if latest_run:
            for cr in latest_run.co_results:
                total_cos_evaluated += 1
                total_attainment_sum += cr.overall_attainment

                sev_key = cr.severity.value
                if sev_key in severity_counts:
                    severity_counts[sev_key] += 1

                if cr.gap_percentage_points <= 0:
                    cos_meeting_target += 1
                else:
                    cos_below_target += 1

                course_code = off.course.code if off.course else ""
                co_label = f"{course_code}-{cr.course_outcome.code if cr.course_outcome else 'CO'}"
                co_bar_data.append({
                    "name": co_label,
                    "target": round(cr.target_attainment, 1),
                    "actual": round(cr.overall_attainment, 1),
                    "gap": round(cr.gap_percentage_points, 1),
                    "level": cr.attainment_level,
                    "severity": cr.severity.value,
                    "blooms": cr.course_outcome.blooms_level if cr.course_outcome else "Apply",
                })

    avg_attainment_rate = (
        round(total_attainment_sum / total_cos_evaluated, 1)
        if total_cos_evaluated > 0 else 0.0
    )

    # Active interventions query
    int_q = db.query(Intervention).filter(
        Intervention.status.in_([InterventionStatus.IDENTIFIED, InterventionStatus.IN_PROGRESS])
    )
    if offering_ids:
        int_q = int_q.filter(Intervention.course_offering_id.in_(offering_ids))
    open_interventions = int_q.count()

    # Improvement calculation from closed/completed interventions
    completed_ints = db.query(Intervention).filter(
        Intervention.status == InterventionStatus.COMPLETED,
        Intervention.improvement_percentage_points.isnot(None)
    )
    if offering_ids:
        completed_ints = completed_ints.filter(Intervention.course_offering_id.in_(offering_ids))
    completed_list = completed_ints.all()

    avg_improvement = (
        round(sum(i.improvement_percentage_points for i in completed_list) / len(completed_list), 1)
        if completed_list else 0.0
    )

    # Donut chart data
    severity_distribution = [
        {"name": "On Target", "value": severity_counts["ON_TARGET"], "color": "#10b981"},
        {"name": "Moderate Gap (<10 pts)", "value": severity_counts["MODERATE"], "color": "#f59e0b"},
        {"name": "High Gap (10-20 pts)", "value": severity_counts["HIGH"], "color": "#f97316"},
        {"name": "Critical Gap (>=20 pts)", "value": severity_counts["CRITICAL"], "color": "#ef4444"},
    ]

    return {
        "kpis": {
            "total_active_courses": total_courses,
            "total_enrolled_students": total_students,
            "cos_evaluated": total_cos_evaluated,
            "overall_attainment_rate": avg_attainment_rate,
            "cos_meeting_target": cos_meeting_target,
            "cos_below_target": cos_below_target,
            "open_interventions": open_interventions,
            "average_improvement_pts": avg_improvement,
        },
        "charts": {
            "co_attainment_bars": co_bar_data[:12],  # up to 12 COs for clean card view
            "severity_distribution": severity_distribution,
        }
    }


@router.get("/semester-trends")
def get_semester_trends(department_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Computes semester-to-semester attainment trend comparison."""
    semesters = db.query(Semester).order_by(Semester.semester_number.asc()).all()
    trend_data = []

    for sem in semesters:
        offerings = db.query(CourseOffering).filter(CourseOffering.semester_id == sem.id).all()
        sem_cos = 0
        sem_sum = 0.0

        for off in offerings:
            latest_run = db.query(AttainmentRun).filter(
                AttainmentRun.course_offering_id == off.id
            ).order_by(AttainmentRun.id.desc()).first()

            if latest_run:
                for cr in latest_run.co_results:
                    sem_cos += 1
                    sem_sum += cr.overall_attainment

        avg_att = round(sem_sum / sem_cos, 1) if sem_cos > 0 else 0.0
        trend_data.append({
            "semester": sem.name,
            "semester_number": sem.semester_number,
            "average_attainment": avg_att,
            "cos_count": sem_cos,
        })

    return trend_data
