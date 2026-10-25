import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.auth import User, UserRole
from backend.app.models.academic import CourseOffering, CourseOutcome, CoPoMapping
from backend.app.models.assessment import Assessment, Question, QuestionCoMapping, StudentMark, IndirectAssessment
from backend.app.models.attainment import (
    AttainmentConfiguration,
    AttainmentRun,
    CoAttainmentResult,
    PoAttainmentResult,
    DirectAttainmentMethod,
    MissingMarkPolicy,
    AttainmentSeverity,
)
from backend.app.schemas.attainment import (
    AttainmentConfigCreate,
    AttainmentConfigResponse,
    AttainmentRunRequest,
    AttainmentRunResponse,
    CoAttainmentResultResponse,
    PoAttainmentResultResponse,
)
from backend.app.services.auth_service import get_current_user, require_roles
from backend.app.analytics.engine import (
    calculate_question_threshold_method,
    calculate_question_normalized_method,
    aggregate_co_question_attainments,
    combine_direct_indirect_attainment,
    classify_attainment_level,
    calculate_gap,
    classify_gap_severity,
    calculate_po_attainment,
    round_num,
)

router = APIRouter(prefix="/attainment", tags=["Attainment Calculation Engine"])


@router.get("/config/{offering_id}", response_model=AttainmentConfigResponse)
def get_attainment_config(offering_id: int, db: Session = Depends(get_db)):
    """Retrieves or creates default attainment configuration for a course offering."""
    config = db.query(AttainmentConfiguration).filter(
        AttainmentConfiguration.course_offering_id == offering_id
    ).first()

    if not config:
        config = AttainmentConfiguration(
            course_offering_id=offering_id,
            direct_method=DirectAttainmentMethod.THRESHOLD,
            threshold_percentage=60.0,
            target_percentage=70.0,
            level1_threshold=60.0,
            level2_threshold=70.0,
            level3_threshold=80.0,
            enable_indirect=1,
            direct_weight=80.0,
            indirect_weight=20.0,
            missing_mark_policy=MissingMarkPolicy.EXCLUDE,
        )
        db.add(config)
        db.commit()
        db.refresh(config)

    return config


@router.post("/config/{offering_id}", response_model=AttainmentConfigResponse)
def save_attainment_config(
    offering_id: int,
    config_in: AttainmentConfigCreate,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """Saves customized attainment thresholds and weighting configuration."""
    config = db.query(AttainmentConfiguration).filter(
        AttainmentConfiguration.course_offering_id == offering_id
    ).first()

    if not config:
        config = AttainmentConfiguration(course_offering_id=offering_id)
        db.add(config)

    for field, val in config_in.model_dump().items():
        setattr(config, field, val)

    db.commit()
    db.refresh(config)
    return config


@router.post("/run", response_model=AttainmentRunResponse)
def run_attainment_calculation(
    run_req: AttainmentRunRequest,
    current_user: User = Depends(require_roles([UserRole.SUPER_ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.HOD, UserRole.FACULTY])),
    db: Session = Depends(get_db)
):
    """
    Executes the pure calculation engine across all assessments, mapped questions,
    and indirect exit surveys for a course offering, creating a versioned snapshot.
    """
    offering = db.query(CourseOffering).filter(CourseOffering.id == run_req.course_offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    # Get configuration
    config = db.query(AttainmentConfiguration).filter(
        AttainmentConfiguration.course_offering_id == offering.id
    ).first()
    if not config:
        config = AttainmentConfiguration(course_offering_id=offering.id)
        db.add(config)
        db.commit()
        db.refresh(config)

    # Fetch COs for this course
    cos = db.query(CourseOutcome).filter(CourseOutcome.course_id == offering.course_id).all()
    if not cos:
        raise HTTPException(status_code=400, detail="No Course Outcomes found for this course.")

    # Fetch all assessments for this offering
    assessments = db.query(Assessment).filter(Assessment.course_offering_id == offering.id).all()
    
    # Pre-calculate each question's attainment
    # Map: question_id -> question_attainment_dict
    question_calc_cache = {}
    for ass in assessments:
        for q in ass.questions:
            # Get marks for question
            marks = db.query(StudentMark).filter(StudentMark.question_id == q.id).all()
            mark_values = [m.marks_obtained for m in marks]
            absent_flags = [m.is_absent for m in marks]

            if config.direct_method == DirectAttainmentMethod.NORMALIZED:
                res = calculate_question_normalized_method(
                    mark_values,
                    absent_flags,
                    max_marks=q.max_marks,
                    missing_mark_policy=config.missing_mark_policy.value
                )
            else:
                res = calculate_question_threshold_method(
                    mark_values,
                    absent_flags,
                    max_marks=q.max_marks,
                    threshold_percentage=config.threshold_percentage,
                    missing_mark_policy=config.missing_mark_policy.value
                )
            question_calc_cache[q.id] = res

    # Create new AttainmentRun record
    run_record = AttainmentRun(
        course_offering_id=offering.id,
        configuration_id=config.id,
        run_timestamp=datetime.now(timezone.utc),
        method_used=config.direct_method.value,
        status="COMPLETED",
        summary_notes=run_req.summary_notes or f"Calculated using {config.direct_method.value} method",
        run_by_user_id=current_user.id,
    )
    db.add(run_record)
    db.flush()

    co_attainments_map = {}
    co_result_records = []

    for co in cos:
        # Find all questions mapped to this CO
        mappings = db.query(QuestionCoMapping).filter(QuestionCoMapping.course_outcome_id == co.id).all()
        
        q_results = []
        eligible_students = 0
        details = []

        for m in mappings:
            q_res = question_calc_cache.get(m.question_id)
            if q_res:
                att_pct = q_res.get("attainment_percentage", 0.0)
                wt = m.weight if m.weight > 0 else 1.0
                q_results.append({"attainment_percentage": att_pct, "weight": wt})
                eligible_students = max(eligible_students, q_res.get("eligible_students", 0))
                details.append({
                    "question_id": m.question_id,
                    "attainment": att_pct,
                    "weight": wt,
                    "eligible": q_res.get("eligible_students", 0),
                    "meeting_threshold": q_res.get("students_meeting_threshold", 0),
                })

        direct_att = aggregate_co_question_attainments(q_results)

        # Check indirect assessment
        indirect_record = db.query(IndirectAssessment).filter(
            IndirectAssessment.course_offering_id == offering.id,
            IndirectAssessment.course_outcome_id == co.id
        ).first()

        indirect_att = indirect_record.attainment_percentage if indirect_record else None

        # Combine direct and indirect
        overall_att = combine_direct_indirect_attainment(
            direct_attainment=direct_att,
            indirect_attainment=indirect_att,
            direct_weight=config.direct_weight,
            indirect_weight=config.indirect_weight,
            enable_indirect=bool(config.enable_indirect)
        )

        # Attainment level
        level = classify_attainment_level(
            overall_att,
            level1_threshold=config.level1_threshold,
            level2_threshold=config.level2_threshold
        )

        # Gap
        target = co.target_attainment_percentage or config.target_percentage
        gap_points = calculate_gap(target, overall_att)
        severity_str = classify_gap_severity(gap_points)

        co_res = CoAttainmentResult(
            attainment_run_id=run_record.id,
            course_outcome_id=co.id,
            direct_attainment=direct_att,
            indirect_attainment=indirect_att,
            overall_attainment=overall_att,
            target_attainment=target,
            attainment_level=level,
            gap_percentage_points=gap_points,
            severity=AttainmentSeverity(severity_str),
            eligible_students_count=eligible_students,
            details_json=json.dumps(details),
        )
        db.add(co_res)
        co_result_records.append(co_res)
        co_attainments_map[co.id] = overall_att

    # Calculate PO/PSO Attainment
    co_po_mappings = db.query(CoPoMapping).join(CourseOutcome).filter(CourseOutcome.course_id == offering.course_id).all()
    po_map_dicts = [
        {"co_id": m.course_outcome_id, "po_id": m.program_outcome_id, "strength": m.mapping_strength}
        for m in co_po_mappings if m.program_outcome_id
    ]
    pso_map_dicts = [
        {"co_id": m.course_outcome_id, "po_id": m.program_specific_outcome_id, "strength": m.mapping_strength}
        for m in co_po_mappings if m.program_specific_outcome_id
    ]

    po_calc_results = calculate_po_attainment(co_attainments_map, po_map_dicts)
    pso_calc_results = calculate_po_attainment(co_attainments_map, pso_map_dicts)

    po_result_records = []
    for po_id, res in po_calc_results.items():
        # Get code
        from backend.app.models.academic import ProgramOutcome
        po_obj = db.query(ProgramOutcome).filter(ProgramOutcome.id == po_id).first()
        code = po_obj.code if po_obj else f"PO_{po_id}"
        
        po_res = PoAttainmentResult(
            attainment_run_id=run_record.id,
            program_outcome_id=po_id,
            outcome_code=code,
            calculated_attainment=res["attainment"],
            average_strength=res["average_strength"],
            mapped_co_count=res["mapped_co_count"],
        )
        db.add(po_res)
        po_result_records.append(po_res)

    for pso_id, res in pso_calc_results.items():
        from backend.app.models.academic import ProgramSpecificOutcome
        pso_obj = db.query(ProgramSpecificOutcome).filter(ProgramSpecificOutcome.id == pso_id).first()
        code = pso_obj.code if pso_obj else f"PSO_{pso_id}"

        pso_res = PoAttainmentResult(
            attainment_run_id=run_record.id,
            program_specific_outcome_id=pso_id,
            outcome_code=code,
            calculated_attainment=res["attainment"],
            average_strength=res["average_strength"],
            mapped_co_count=res["mapped_co_count"],
        )
        db.add(pso_res)
        po_result_records.append(pso_res)

    db.commit()
    db.refresh(run_record)

    from backend.app.routers.audit import log_audit_event, create_notification
    log_audit_event(
        db,
        action="CALCULATE_ATTAINMENT",
        user_id=current_user.id,
        entity_type="COURSE_OFFERING",
        entity_id=str(offering.id),
        details={"run_id": run_record.id, "method": config.direct_method.value, "co_count": len(cos)}
    )
    create_notification(
        db,
        title="Attainment Calculation Complete",
        message=f"OBE attainment calculation snapshot #{run_record.id} generated for {offering.course.code if offering.course else 'course'}.",
        user_id=current_user.id,
        notification_type="SUCCESS",
        link="/attainment",
    )

    # Format response
    co_resp = []
    for cr in run_record.co_results:
        co_resp.append(CoAttainmentResultResponse(
            id=cr.id,
            course_outcome_id=cr.course_outcome_id,
            co_code=cr.course_outcome.code if cr.course_outcome else "",
            co_description=cr.course_outcome.description if cr.course_outcome else "",
            blooms_level=cr.course_outcome.blooms_level if cr.course_outcome else "",
            direct_attainment=cr.direct_attainment,
            indirect_attainment=cr.indirect_attainment,
            overall_attainment=cr.overall_attainment,
            target_attainment=cr.target_attainment,
            attainment_level=cr.attainment_level,
            gap_percentage_points=cr.gap_percentage_points,
            severity=cr.severity,
            eligible_students_count=cr.eligible_students_count,
            details_json=cr.details_json,
        ))

    po_resp = [
        PoAttainmentResultResponse(
            id=pr.id,
            outcome_code=pr.outcome_code,
            calculated_attainment=pr.calculated_attainment,
            average_strength=pr.average_strength,
            mapped_co_count=pr.mapped_co_count,
        )
        for pr in run_record.po_results
    ]

    return AttainmentRunResponse(
        id=run_record.id,
        course_offering_id=run_record.course_offering_id,
        configuration_id=run_record.configuration_id,
        run_timestamp=run_record.run_timestamp,
        method_used=run_record.method_used,
        status=run_record.status,
        summary_notes=run_record.summary_notes,
        co_results=co_resp,
        po_results=po_resp,
    )


@router.get("/offerings/{offering_id}/latest", response_model=Optional[AttainmentRunResponse])
def get_latest_attainment_run(offering_id: int, db: Session = Depends(get_db)):
    """Retrieves the most recent calculation run results for a course offering."""
    latest_run = db.query(AttainmentRun).filter(
        AttainmentRun.course_offering_id == offering_id
    ).order_by(AttainmentRun.id.desc()).first()

    if not latest_run:
        return None

    co_resp = []
    for cr in latest_run.co_results:
        co_resp.append(CoAttainmentResultResponse(
            id=cr.id,
            course_outcome_id=cr.course_outcome_id,
            co_code=cr.course_outcome.code if cr.course_outcome else "",
            co_description=cr.course_outcome.description if cr.course_outcome else "",
            blooms_level=cr.course_outcome.blooms_level if cr.course_outcome else "",
            direct_attainment=cr.direct_attainment,
            indirect_attainment=cr.indirect_attainment,
            overall_attainment=cr.overall_attainment,
            target_attainment=cr.target_attainment,
            attainment_level=cr.attainment_level,
            gap_percentage_points=cr.gap_percentage_points,
            severity=cr.severity,
            eligible_students_count=cr.eligible_students_count,
            details_json=cr.details_json,
        ))

    po_resp = [
        PoAttainmentResultResponse(
            id=pr.id,
            outcome_code=pr.outcome_code,
            calculated_attainment=pr.calculated_attainment,
            average_strength=pr.average_strength,
            mapped_co_count=pr.mapped_co_count,
        )
        for pr in latest_run.po_results
    ]

    return AttainmentRunResponse(
        id=latest_run.id,
        course_offering_id=latest_run.course_offering_id,
        configuration_id=latest_run.configuration_id,
        run_timestamp=latest_run.run_timestamp,
        method_used=latest_run.method_used,
        status=latest_run.status,
        summary_notes=latest_run.summary_notes,
        co_results=co_resp,
        po_results=po_resp,
    )
