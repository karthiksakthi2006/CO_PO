"""
CO-ATTAIN PRO AI - Pure Calculation Engine
Academic Attainment Analytics & OBE Calculations

Implements Method A (Student Threshold Method) and Method B (Normalized Score Method),
CO Aggregation, Assessment Component Aggregation, Direct/Indirect Weighting,
Attainment Levels, and Program Outcome (PO/PSO) Mapping Attainment.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP


def round_num(value: float, decimals: int = 2) -> float:
    """Helper to round float values reliably using ROUND_HALF_UP."""
    if value is None:
        return 0.0
    d = Decimal(str(value))
    format_str = "0." + "0" * decimals if decimals > 0 else "0"
    return float(d.quantize(Decimal(format_str), rounding=ROUND_HALF_UP))


def calculate_question_threshold_method(
    student_marks: List[Optional[float]],
    is_absent_list: List[bool],
    max_marks: float,
    threshold_percentage: float = 60.0,
    missing_mark_policy: str = "EXCLUDE"
) -> Dict[str, Any]:
    """
    Method A: Student Threshold Method.
    
    Formula:
      eligible_students = students with valid marks under missing/absence policy
      students_meeting_threshold = eligible students with score >= (threshold_pct / 100) * max_marks
      attainment_pct = (students_meeting_threshold / eligible_students) * 100
    """
    if max_marks <= 0:
        return {
            "eligible_students": 0,
            "absent_students": 0,
            "students_meeting_threshold": 0,
            "attainment_percentage": 0.0,
            "threshold_score_required": 0.0,
            "error": "Question maximum marks must be strictly greater than 0"
        }

    threshold_score = (threshold_percentage / 100.0) * max_marks
    eligible_students = 0
    absent_count = 0
    meeting_threshold = 0

    for mark, absent in zip(student_marks, is_absent_list):
        if absent or mark is None:
            absent_count += 1
            if missing_mark_policy.upper() == "ZERO":
                eligible_students += 1
                effective_mark = 0.0
                if effective_mark >= threshold_score:
                    meeting_threshold += 1
            else:
                # EXCLUDE: student is excluded from both numerator and denominator
                continue
        else:
            eligible_students += 1
            if mark >= threshold_score:
                meeting_threshold += 1

    attainment_pct = 0.0
    if eligible_students > 0:
        attainment_pct = (meeting_threshold / eligible_students) * 100.0

    return {
        "eligible_students": eligible_students,
        "absent_students": absent_count,
        "students_meeting_threshold": meeting_threshold,
        "threshold_percentage": threshold_percentage,
        "threshold_score_required": round_num(threshold_score, 2),
        "attainment_percentage": round_num(attainment_pct, 2),
        "method": "THRESHOLD"
    }


def calculate_question_normalized_method(
    student_marks: List[Optional[float]],
    is_absent_list: List[bool],
    max_marks: float,
    missing_mark_policy: str = "EXCLUDE"
) -> Dict[str, Any]:
    """
    Method B: Normalized Score Method.
    
    Formula:
      question_attainment_percentage = (sum of valid student marks / sum of corresponding maximum marks) * 100
    """
    if max_marks <= 0:
        return {
            "eligible_students": 0,
            "absent_students": 0,
            "total_marks_obtained": 0.0,
            "total_max_marks": 0.0,
            "attainment_percentage": 0.0,
            "error": "Question maximum marks must be strictly greater than 0"
        }

    total_obtained = 0.0
    total_max = 0.0
    eligible_students = 0
    absent_count = 0

    for mark, absent in zip(student_marks, is_absent_list):
        if absent or mark is None:
            absent_count += 1
            if missing_mark_policy.upper() == "ZERO":
                eligible_students += 1
                total_obtained += 0.0
                total_max += max_marks
            else:
                continue
        else:
            eligible_students += 1
            total_obtained += mark
            total_max += max_marks

    attainment_pct = 0.0
    if total_max > 0:
        attainment_pct = (total_obtained / total_max) * 100.0

    return {
        "eligible_students": eligible_students,
        "absent_students": absent_count,
        "total_marks_obtained": round_num(total_obtained, 2),
        "total_max_marks": round_num(total_max, 2),
        "attainment_percentage": round_num(attainment_pct, 2),
        "method": "NORMALIZED"
    }


def aggregate_co_question_attainments(
    question_results: List[Dict[str, Any]]
) -> float:
    """
    Aggregates question attainments mapped to a single CO using their weights.
    
    Each item in question_results should contain:
      - 'attainment_percentage': float
      - 'weight': float (default 1.0)
    
    Formula:
      sum(attainment_i * weight_i) / sum(weight_i)
    """
    total_weighted_attainment = 0.0
    total_weight = 0.0

    for q in question_results:
        att = q.get("attainment_percentage", 0.0)
        wt = q.get("weight", 1.0)
        if wt > 0:
            total_weighted_attainment += att * wt
            total_weight += wt

    if total_weight <= 0:
        return 0.0

    return round_num(total_weighted_attainment / total_weight, 2)


def combine_direct_indirect_attainment(
    direct_attainment: float,
    indirect_attainment: Optional[float],
    direct_weight: float = 80.0,
    indirect_weight: float = 20.0,
    enable_indirect: bool = True
) -> float:
    """
    Combines direct and indirect attainment based on approved institution weights.
    
    Formula:
      overall = (direct * direct_weight + indirect * indirect_weight) / (direct_weight + indirect_weight)
    
    If indirect attainment is disabled or None, overall direct attainment is used without fabrication.
    """
    if not enable_indirect or indirect_attainment is None:
        return round_num(direct_attainment, 2)

    total_weight = direct_weight + indirect_weight
    if total_weight <= 0:
        return round_num(direct_attainment, 2)

    overall = (direct_attainment * direct_weight + indirect_attainment * indirect_weight) / total_weight
    return round_num(overall, 2)


def classify_attainment_level(
    attainment_percentage: float,
    level1_threshold: float = 60.0,
    level2_threshold: float = 70.0
) -> int:
    """
    Classifies attainment percentage into academic levels:
      Level 1: < level1_threshold (e.g., < 60%)
      Level 2: level1_threshold <= attainment < level2_threshold (e.g., 60% - 69.99%)
      Level 3: >= level2_threshold (e.g., >= 70%)
    """
    if attainment_percentage >= level2_threshold:
        return 3
    elif attainment_percentage >= level1_threshold:
        return 2
    else:
        return 1


def calculate_gap(target_percentage: float, actual_percentage: float) -> float:
    """
    Calculates gap in percentage points:
      gap_percentage_points = target_attainment - actual_attainment
      
      positive gap = below target
      zero gap = target met exactly
      negative gap = target exceeded
    """
    return round_num(target_percentage - actual_percentage, 2)


def classify_gap_severity(gap_points: float) -> str:
    """
    Categorizes gap severity based on percentage points below target:
      - Critical: gap >= 20 percentage points
      - High: 10 <= gap < 20 percentage points
      - Moderate: 0 < gap < 10 percentage points
      - On Target: gap <= 0
    """
    if gap_points <= 0:
        return "ON_TARGET"
    elif gap_points < 10.0:
        return "MODERATE"
    elif gap_points < 20.0:
        return "HIGH"
    else:
        return "CRITICAL"


def calculate_po_attainment(
    co_attainments: Dict[int, float],  # co_id -> attainment_percentage
    po_mappings: List[Dict[str, Any]]   # list of {co_id, po_id, strength: 0..3}
) -> Dict[int, Dict[str, Any]]:
    """
    Calculates Program Outcome (PO/PSO) attainment from CO attainments and mapping matrix.
    
    Formula:
      PO_j attainment = sum(CO_i * strength_ij) / sum(strength_ij) for all mapped COs with strength > 0.
      Average strength = sum(strength_ij) / count(mapped COs with strength > 0)
    """
    po_aggregates: Dict[int, Dict[str, Any]] = {}

    for mapping in po_mappings:
        co_id = mapping.get("co_id")
        po_id = mapping.get("po_id")
        strength = mapping.get("strength", 0)

        if po_id is None or strength <= 0:
            continue

        co_att = co_attainments.get(co_id)
        if co_att is None:
            continue

        if po_id not in po_aggregates:
            po_aggregates[po_id] = {
                "weighted_sum": 0.0,
                "total_strength": 0.0,
                "mapped_co_count": 0,
            }

        po_aggregates[po_id]["weighted_sum"] += co_att * strength
        po_aggregates[po_id]["total_strength"] += strength
        po_aggregates[po_id]["mapped_co_count"] += 1

    results: Dict[int, Dict[str, Any]] = {}
    for po_id, agg in po_aggregates.items():
        total_str = agg["total_strength"]
        co_count = agg["mapped_co_count"]
        
        attainment = 0.0
        avg_strength = 0.0
        if total_str > 0:
            attainment = round_num(agg["weighted_sum"] / total_str, 2)
            avg_strength = round_num(total_str / co_count, 2) if co_count > 0 else 0.0

        results[po_id] = {
            "attainment": attainment,
            "average_strength": avg_strength,
            "mapped_co_count": co_count,
        }

    return results


def calculate_improvement_percentage_points(
    pre_attainment: float,
    post_attainment: Optional[float]
) -> Optional[float]:
    """
    Calculates improvement following an intervention:
      improvement = post_intervention_attainment - pre_intervention_attainment
    """
    if post_attainment is None:
        return None
    return round_num(post_attainment - pre_attainment, 2)
