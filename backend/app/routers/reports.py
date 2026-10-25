from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.academic import CourseOffering
from backend.app.models.attainment import AttainmentRun, AttainmentConfiguration
from backend.app.models.intervention import Intervention
from backend.app.services.report_service import (
    generate_attainment_pdf_report,
    generate_attainment_excel_report,
)

router = APIRouter(prefix="/reports", tags=["Reports & Accreditation Exports"])


@router.get("/offerings/{offering_id}/pdf")
def download_course_attainment_pdf(offering_id: int, db: Session = Depends(get_db)):
    """Downloads official NBA/NAAC Course Outcome Attainment & Gap Analysis Report in PDF format."""
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    latest_run = db.query(AttainmentRun).filter(
        AttainmentRun.course_offering_id == offering_id
    ).order_by(AttainmentRun.id.desc()).first()

    if not latest_run:
        raise HTTPException(status_code=400, detail="No calculation runs available. Please run attainment calculation first.")

    course_data = {
        "institution_name": offering.course.department.institution.name if offering.course and offering.course.department and offering.course.department.institution else "Apex Institute of Technology",
        "department_name": offering.course.department.name if offering.course and offering.course.department else "Department of Computer Science & Engineering",
        "course_code": offering.course.code if offering.course else "",
        "course_name": offering.course.name if offering.course else "",
        "academic_year": offering.academic_year.name if offering.academic_year else "2024-2025",
        "semester_name": offering.semester.name if offering.semester else "Semester 5",
        "section": offering.section,
        "faculty_name": offering.faculty.full_name if offering.faculty else "Dr. Sarah Jenkins",
    }

    config_dict = {
        "direct_method": latest_run.configuration.direct_method.value if latest_run.configuration else "THRESHOLD",
        "threshold_percentage": latest_run.configuration.threshold_percentage if latest_run.configuration else 60.0,
        "direct_weight": latest_run.configuration.direct_weight if latest_run.configuration else 80.0,
        "indirect_weight": latest_run.configuration.indirect_weight if latest_run.configuration else 20.0,
    }

    co_results = [
        {
            "co_code": cr.course_outcome.code if cr.course_outcome else "",
            "blooms_level": cr.course_outcome.blooms_level if cr.course_outcome else "Apply",
            "target_attainment": cr.target_attainment,
            "direct_attainment": cr.direct_attainment,
            "indirect_attainment": cr.indirect_attainment,
            "overall_attainment": cr.overall_attainment,
            "attainment_level": cr.attainment_level,
            "gap_percentage_points": cr.gap_percentage_points,
            "severity": cr.severity.value,
        }
        for cr in latest_run.co_results
    ]

    po_results = [
        {
            "outcome_code": pr.outcome_code,
            "calculated_attainment": pr.calculated_attainment,
            "average_strength": pr.average_strength,
            "mapped_co_count": pr.mapped_co_count,
        }
        for pr in latest_run.po_results
    ]

    interventions = [
        {
            "co_code": i.course_outcome.code if i.course_outcome else "",
            "gap_percentage_points": i.gap_percentage_points,
            "action_plan": i.action_plan,
            "pre_intervention_attainment": i.pre_intervention_attainment,
            "post_intervention_attainment": i.post_intervention_attainment,
            "improvement_percentage_points": i.improvement_percentage_points,
            "status": i.status.value,
        }
        for i in offering.interventions
    ]

    pdf_bytes = generate_attainment_pdf_report(
        course_data=course_data,
        co_results=co_results,
        po_results=po_results,
        gaps=[],
        interventions=interventions,
        config=config_dict,
    )

    filename = f"CO_Attainment_Report_{course_data['course_code']}_{offering.section}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/offerings/{offering_id}/excel")
def download_course_attainment_excel(offering_id: int, db: Session = Depends(get_db)):
    """Downloads Course Outcome and PO-PSO Attainment data in Excel format."""
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    latest_run = db.query(AttainmentRun).filter(
        AttainmentRun.course_offering_id == offering_id
    ).order_by(AttainmentRun.id.desc()).first()

    if not latest_run:
        raise HTTPException(status_code=400, detail="No calculation runs available.")

    course_data = {
        "course_code": offering.course.code if offering.course else "",
        "course_name": offering.course.name if offering.course else "",
    }

    co_results = [
        {
            "co_code": cr.course_outcome.code if cr.course_outcome else "",
            "blooms_level": cr.course_outcome.blooms_level if cr.course_outcome else "Apply",
            "target_attainment": cr.target_attainment,
            "direct_attainment": cr.direct_attainment,
            "indirect_attainment": cr.indirect_attainment,
            "overall_attainment": cr.overall_attainment,
            "attainment_level": cr.attainment_level,
            "gap_percentage_points": cr.gap_percentage_points,
            "severity": cr.severity.value,
        }
        for cr in latest_run.co_results
    ]

    po_results = [
        {
            "outcome_code": pr.outcome_code,
            "calculated_attainment": pr.calculated_attainment,
            "average_strength": pr.average_strength,
            "mapped_co_count": pr.mapped_co_count,
        }
        for pr in latest_run.po_results
    ]

    excel_bytes = generate_attainment_excel_report(course_data, co_results, po_results)
    filename = f"CO_Attainment_{course_data['course_code']}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
