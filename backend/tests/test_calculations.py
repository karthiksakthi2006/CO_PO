"""
Unit Tests for Calculation Engine
Validates all formulas, edge cases, threshold methods, absent policies, and gap metrics.
"""

import pytest
from backend.app.analytics.engine import (
    calculate_question_threshold_method,
    calculate_question_normalized_method,
    aggregate_co_question_attainments,
    combine_direct_indirect_attainment,
    classify_attainment_level,
    calculate_gap,
    classify_gap_severity,
    calculate_po_attainment,
    calculate_improvement_percentage_points,
    round_num,
)


def test_threshold_method_basic():
    # 5 students, max marks 10, threshold 60% (>= 6.0)
    # Marks: [7.0, 6.0, 5.0, 8.0, 4.0] -> 3 students meet threshold (7.0, 6.0, 8.0)
    # Attainment = 3 / 5 * 100 = 60.0%
    marks = [7.0, 6.0, 5.0, 8.0, 4.0]
    absent = [False, False, False, False, False]
    res = calculate_question_threshold_method(marks, absent, max_marks=10.0, threshold_percentage=60.0)
    assert res["eligible_students"] == 5
    assert res["students_meeting_threshold"] == 3
    assert res["attainment_percentage"] == 60.0
    assert res["threshold_score_required"] == 6.0


def test_threshold_method_with_absent_exclude():
    # 5 students, 1 absent. Policy: EXCLUDE
    # Marks: [8.0, 9.0, 2.0, None, 7.0]
    # Eligible = 4 (None excluded). Meeting >= 6.0: 8.0, 9.0, 7.0 (3 students)
    # Attainment = 3 / 4 * 100 = 75.0%
    marks = [8.0, 9.0, 2.0, None, 7.0]
    absent = [False, False, False, True, False]
    res = calculate_question_threshold_method(marks, absent, max_marks=10.0, threshold_percentage=60.0, missing_mark_policy="EXCLUDE")
    assert res["eligible_students"] == 4
    assert res["absent_students"] == 1
    assert res["students_meeting_threshold"] == 3
    assert res["attainment_percentage"] == 75.0


def test_threshold_method_with_absent_zero():
    # Same as above, but Policy: ZERO
    # Eligible = 5 (Absent included as 0). Meeting >= 6.0: 3 students
    # Attainment = 3 / 5 * 100 = 60.0%
    marks = [8.0, 9.0, 2.0, None, 7.0]
    absent = [False, False, False, True, False]
    res = calculate_question_threshold_method(marks, absent, max_marks=10.0, threshold_percentage=60.0, missing_mark_policy="ZERO")
    assert res["eligible_students"] == 5
    assert res["absent_students"] == 1
    assert res["students_meeting_threshold"] == 3
    assert res["attainment_percentage"] == 60.0


def test_normalized_score_method():
    # 4 students, max marks 20
    # Marks: [15, 10, 20, 15] -> sum = 60. Total max = 4 * 20 = 80.
    # Attainment = (60 / 80) * 100 = 75.0%
    marks = [15.0, 10.0, 20.0, 15.0]
    absent = [False, False, False, False]
    res = calculate_question_normalized_method(marks, absent, max_marks=20.0)
    assert res["eligible_students"] == 4
    assert res["total_marks_obtained"] == 60.0
    assert res["total_max_marks"] == 80.0
    assert res["attainment_percentage"] == 75.0


def test_invalid_max_marks():
    res1 = calculate_question_threshold_method([5.0], [False], max_marks=0.0)
    assert res1["attainment_percentage"] == 0.0
    assert "error" in res1

    res2 = calculate_question_normalized_method([5.0], [False], max_marks=-5.0)
    assert res2["attainment_percentage"] == 0.0
    assert "error" in res2


def test_zero_eligible_students():
    res = calculate_question_threshold_method([], [], max_marks=10.0)
    assert res["eligible_students"] == 0
    assert res["attainment_percentage"] == 0.0


def test_aggregate_co_questions():
    # Q1: 80% (wt: 1.0), Q2: 60% (wt: 1.0) -> (80 + 60)/2 = 70.0%
    q_results = [
        {"attainment_percentage": 80.0, "weight": 1.0},
        {"attainment_percentage": 60.0, "weight": 1.0},
    ]
    assert aggregate_co_question_attainments(q_results) == 70.0

    # Weighted: Q1: 80% (wt 2.0), Q2: 50% (wt 1.0) -> (160 + 50)/3 = 210/3 = 70.0%
    q_results_weighted = [
        {"attainment_percentage": 80.0, "weight": 2.0},
        {"attainment_percentage": 50.0, "weight": 1.0},
    ]
    assert aggregate_co_question_attainments(q_results_weighted) == 70.0

    # Zero total weight
    assert aggregate_co_question_attainments([{"attainment_percentage": 80.0, "weight": 0.0}]) == 0.0


def test_combine_direct_indirect_attainment():
    # Direct = 80.0%, Indirect = 60.0%, Weights: 80% direct, 20% indirect
    # Overall = (80 * 80 + 60 * 20) / 100 = (6400 + 1200) / 100 = 76.0%
    overall = combine_direct_indirect_attainment(80.0, 60.0, direct_weight=80.0, indirect_weight=20.0, enable_indirect=True)
    assert overall == 76.0

    # When indirect is None or disabled, direct is returned without fabrication
    assert combine_direct_indirect_attainment(80.0, None) == 80.0
    assert combine_direct_indirect_attainment(80.0, 60.0, enable_indirect=False) == 80.0


def test_attainment_levels():
    # Default thresholds: level1 < 60, level2 60..70, level3 >= 70
    assert classify_attainment_level(59.9, 60.0, 70.0) == 1
    assert classify_attainment_level(60.0, 60.0, 70.0) == 2
    assert classify_attainment_level(69.99, 60.0, 70.0) == 2
    assert classify_attainment_level(70.0, 60.0, 70.0) == 3
    assert classify_attainment_level(85.5, 60.0, 70.0) == 3


def test_gap_calculation_and_severity():
    # Target = 70.0
    # Case 1: Exceeded (actual = 75.0) -> gap = -5.0 -> ON_TARGET
    gap1 = calculate_gap(70.0, 75.0)
    assert gap1 == -5.0
    assert classify_gap_severity(gap1) == "ON_TARGET"

    # Case 2: Met exactly (actual = 70.0) -> gap = 0.0 -> ON_TARGET
    gap2 = calculate_gap(70.0, 70.0)
    assert gap2 == 0.0
    assert classify_gap_severity(gap2) == "ON_TARGET"

    # Case 3: Moderate gap (actual = 65.0) -> gap = 5.0 -> MODERATE (0 < gap < 10)
    gap3 = calculate_gap(70.0, 65.0)
    assert gap3 == 5.0
    assert classify_gap_severity(gap3) == "MODERATE"

    # Case 4: High gap (actual = 55.0) -> gap = 15.0 -> HIGH (10 <= gap < 20)
    gap4 = calculate_gap(70.0, 55.0)
    assert gap4 == 15.0
    assert classify_gap_severity(gap4) == "HIGH"

    # Case 5: Critical gap (actual = 48.0) -> gap = 22.0 -> CRITICAL (gap >= 20)
    gap5 = calculate_gap(70.0, 48.0)
    assert gap5 == 22.0
    assert classify_gap_severity(gap5) == "CRITICAL"


def test_po_attainment_calculation():
    # CO1 attainment = 80%, CO2 attainment = 60%
    # PO1 mapped to CO1 (strength 3) and CO2 (strength 2)
    # PO1 attainment = (80 * 3 + 60 * 2) / (3 + 2) = (240 + 120) / 5 = 72.0%
    # Average strength = 5 / 2 = 2.5
    co_attainments = {1: 80.0, 2: 60.0}
    po_mappings = [
        {"co_id": 1, "po_id": 101, "strength": 3},
        {"co_id": 2, "po_id": 101, "strength": 2},
        {"co_id": 1, "po_id": 102, "strength": 0},  # unmapped (strength 0)
    ]
    res = calculate_po_attainment(co_attainments, po_mappings)
    assert 101 in res
    assert res[101]["attainment"] == 72.0
    assert res[101]["average_strength"] == 2.5
    assert res[101]["mapped_co_count"] == 2
    assert 102 not in res  # zero strength should not be considered mapped


def test_improvement_calculation():
    pre = 48.0
    post = 65.0
    assert calculate_improvement_percentage_points(pre, post) == 17.0
    assert calculate_improvement_percentage_points(pre, None) is None
