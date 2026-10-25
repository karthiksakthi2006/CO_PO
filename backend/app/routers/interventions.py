from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.models.academic import CourseOffering, CourseOutcome
from backend.app.models.intervention import Intervention, Reassessment, InterventionStatus, EffectivenessRating
from backend.app.schemas.intervention import (
    InterventionCreate,
    InterventionUpdate,
    InterventionResponse,
    ReassessmentCreate,
    ReassessmentResponse,
)
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.analytics.engine import calculate_improvement_percentage_points

router = APIRouter(prefix="/interventions", tags=["Continuous Improvement (CQI) Workflows"])


@router.get("/offerings/{offering_id}", response_model=List[InterventionResponse])
def get_interventions(offering_id: int, db: Session = Depends(get_db)):
    """Retrieves all academic remedial interventions for a course offering."""
    interventions = db.query(Intervention).filter(Intervention.course_offering_id == offering_id).all()
    results = []
    for item in interventions:
        results.append(InterventionResponse(
            id=item.id,
            course_offering_id=item.course_offering_id,
            course_outcome_id=item.course_outcome_id,
            co_code=item.course_outcome.code if item.course_outcome else "",
            gap_percentage_points=item.gap_percentage_points,
            severity=item.severity,
            root_cause_analysis=item.root_cause_analysis,
            action_plan=item.action_plan,
            pedagogical_tool=item.pedagogical_tool,
            assigned_faculty_id=item.assigned_faculty_id,
            assigned_faculty_name=item.assigned_faculty.full_name if item.assigned_faculty else "Unassigned",
            target_completion_date=item.target_completion_date,
            status=item.status,
            pre_intervention_attainment=item.pre_intervention_attainment,
            post_intervention_attainment=item.post_intervention_attainment,
            improvement_percentage_points=item.improvement_percentage_points,
            effectiveness_rating=item.effectiveness_rating,
            created_at=item.created_at,
            updated_at=item.updated_at,
            reassessments=[
                ReassessmentResponse(
                    id=r.id,
                    intervention_id=r.intervention_id,
                    assessment_name=r.assessment_name,
                    conduct_date=r.conduct_date,
                    total_students=r.total_students,
                    students_passed=r.students_passed,
                    average_score=r.average_score,
                    reassessment_attainment=r.reassessment_attainment,
                    notes=r.notes,
                )
                for r in item.reassessments
            ],
        ))
    return results


@router.post("", response_model=InterventionResponse)
def create_intervention(
    int_in: InterventionCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Creates a new remedial intervention plan."""
    intervention = Intervention(
        course_offering_id=int_in.course_offering_id,
        course_outcome_id=int_in.course_outcome_id,
        gap_percentage_points=int_in.gap_percentage_points,
        severity=int_in.severity,
        root_cause_analysis=int_in.root_cause_analysis,
        action_plan=int_in.action_plan,
        pedagogical_tool=int_in.pedagogical_tool,
        assigned_faculty_id=int_in.assigned_faculty_id or current_user.id,
        target_completion_date=int_in.target_completion_date,
        status=InterventionStatus.IN_PROGRESS,
        pre_intervention_attainment=int_in.pre_intervention_attainment,
        effectiveness_rating=EffectivenessRating.PENDING_REASSESSMENT,
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)

    from backend.app.routers.audit import log_audit_event, create_notification
    log_audit_event(
        db,
        action="CREATE_INTERVENTION",
        user_id=current_user.id,
        entity_type="INTERVENTION",
        entity_id=str(intervention.id),
        details={"co_id": intervention.course_outcome_id, "gap": intervention.gap_percentage_points}
    )
    create_notification(
        db,
        title="Remedial Intervention Created",
        message=f"CQI Action Plan created for {intervention.course_outcome.code if intervention.course_outcome else 'CO'}.",
        user_id=current_user.id,
        notification_type="WARNING" if intervention.gap_percentage_points >= 20 else "INFO",
        link="/interventions",
    )

    return InterventionResponse(
        id=intervention.id,
        course_offering_id=intervention.course_offering_id,
        course_outcome_id=intervention.course_outcome_id,
        co_code=intervention.course_outcome.code if intervention.course_outcome else "",
        gap_percentage_points=intervention.gap_percentage_points,
        severity=intervention.severity,
        root_cause_analysis=intervention.root_cause_analysis,
        action_plan=intervention.action_plan,
        pedagogical_tool=intervention.pedagogical_tool,
        assigned_faculty_id=intervention.assigned_faculty_id,
        assigned_faculty_name=intervention.assigned_faculty.full_name if intervention.assigned_faculty else "Unassigned",
        target_completion_date=intervention.target_completion_date,
        status=intervention.status,
        pre_intervention_attainment=intervention.pre_intervention_attainment,
        post_intervention_attainment=intervention.post_intervention_attainment,
        improvement_percentage_points=intervention.improvement_percentage_points,
        effectiveness_rating=intervention.effectiveness_rating,
        created_at=intervention.created_at,
        updated_at=intervention.updated_at,
        reassessments=[],
    )


@router.patch("/{intervention_id}", response_model=InterventionResponse)
def update_intervention(
    intervention_id: int,
    update_in: InterventionUpdate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Updates status or manual post-intervention assessment metrics."""
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    if update_in.status is not None:
        intervention.status = update_in.status
    if update_in.action_plan is not None:
        intervention.action_plan = update_in.action_plan
    if update_in.post_intervention_attainment is not None:
        intervention.post_intervention_attainment = update_in.post_intervention_attainment
        intervention.improvement_percentage_points = calculate_improvement_percentage_points(
            intervention.pre_intervention_attainment,
            update_in.post_intervention_attainment
        )
    if update_in.effectiveness_rating is not None:
        intervention.effectiveness_rating = update_in.effectiveness_rating

    intervention.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(intervention)

    return InterventionResponse(
        id=intervention.id,
        course_offering_id=intervention.course_offering_id,
        course_outcome_id=intervention.course_outcome_id,
        co_code=intervention.course_outcome.code if intervention.course_outcome else "",
        gap_percentage_points=intervention.gap_percentage_points,
        severity=intervention.severity,
        root_cause_analysis=intervention.root_cause_analysis,
        action_plan=intervention.action_plan,
        pedagogical_tool=intervention.pedagogical_tool,
        assigned_faculty_id=intervention.assigned_faculty_id,
        assigned_faculty_name=intervention.assigned_faculty.full_name if intervention.assigned_faculty else "Unassigned",
        target_completion_date=intervention.target_completion_date,
        status=intervention.status,
        pre_intervention_attainment=intervention.pre_intervention_attainment,
        post_intervention_attainment=intervention.post_intervention_attainment,
        improvement_percentage_points=intervention.improvement_percentage_points,
        effectiveness_rating=intervention.effectiveness_rating,
        created_at=intervention.created_at,
        updated_at=intervention.updated_at,
        reassessments=[],
    )


@router.post("/{intervention_id}/reassessments", response_model=ReassessmentResponse)
def record_reassessment(
    intervention_id: int,
    reass_in: ReassessmentCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """
    Records a post-remedial test / reassessment and updates the intervention's
    post-intervention attainment, calculated improvement, and effectiveness status.
    """
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")

    reass = Reassessment(
        intervention_id=intervention_id,
        assessment_name=reass_in.assessment_name,
        conduct_date=reass_in.conduct_date or datetime.now(timezone.utc),
        total_students=reass_in.total_students,
        students_passed=reass_in.students_passed,
        average_score=reass_in.average_score,
        reassessment_attainment=reass_in.reassessment_attainment,
        notes=reass_in.notes,
    )
    db.add(reass)

    # Update intervention post-attainment and improvement
    intervention.post_intervention_attainment = reass_in.reassessment_attainment
    improvement = calculate_improvement_percentage_points(
        intervention.pre_intervention_attainment,
        reass_in.reassessment_attainment
    )
    intervention.improvement_percentage_points = improvement

    # Determine effectiveness
    if improvement and improvement >= 15.0:
        intervention.effectiveness_rating = EffectivenessRating.EFFECTIVE
        intervention.status = InterventionStatus.COMPLETED
    elif improvement and improvement > 0.0:
        intervention.effectiveness_rating = EffectivenessRating.PARTIALLY_EFFECTIVE
        intervention.status = InterventionStatus.COMPLETED
    else:
        intervention.effectiveness_rating = EffectivenessRating.NEEDS_FURTHER_ACTION

    intervention.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(reass)

    return ReassessmentResponse(
        id=reass.id,
        intervention_id=reass.intervention_id,
        assessment_name=reass.assessment_name,
        conduct_date=reass.conduct_date,
        total_students=reass.total_students,
        students_passed=reass.students_passed,
        average_score=reass.average_score,
        reassessment_attainment=reass.reassessment_attainment,
        notes=reass.notes,
    )
