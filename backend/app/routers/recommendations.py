from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.academic import CourseOffering
from backend.app.models.attainment import AttainmentRun
from backend.app.services.recommendation_service import generate_rule_based_recommendations

router = APIRouter(prefix="/recommendations", tags=["Pedagogical Recommendations"])


@router.get("/offerings/{offering_id}")
def get_course_recommendations(offering_id: int, db: Session = Depends(get_db)):
    """
    Generates explainable pedagogical recommendations mapped to Bloom's Taxonomy
    for all Course Outcomes exhibiting performance gaps.
    """
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    course_name = f"{offering.course.code}: {offering.course.name}" if offering.course else "Course"

    latest_run = db.query(AttainmentRun).filter(
        AttainmentRun.course_offering_id == offering_id
    ).order_by(AttainmentRun.id.desc()).first()

    if not latest_run:
        return {
            "has_data": False,
            "message": "Calculate attainment first to generate targeted recommendations.",
            "recommendations": [],
        }

    co_gaps = []
    for cr in latest_run.co_results:
        if cr.gap_percentage_points > 0:
            co_gaps.append({
                "course_outcome_id": cr.course_outcome_id,
                "co_code": cr.course_outcome.code if cr.course_outcome else "",
                "blooms_level": cr.course_outcome.blooms_level if cr.course_outcome else "Apply",
                "gap_percentage_points": cr.gap_percentage_points,
                "severity": cr.severity.value,
                "target_attainment": cr.target_attainment,
                "actual_attainment": cr.overall_attainment,
            })

    recs = generate_rule_based_recommendations(co_gaps, course_name=course_name)

    return {
        "has_data": True,
        "course_name": course_name,
        "recommendations": recs,
        "engine_type": "Deterministic Bloom's Cognitive Taxonomy Engine",
        "advisory_note": "Recommendations are based on measured gap severity and Bloom's cognitive domain mapping.",
    }
