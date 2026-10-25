"""
CO-ATTAIN PRO AI - Academic Gap Detection & Insights Engine
Analyzes attainment results, questions, components, and student trends to identify learning gaps
with transparent, explainable evidence.
"""

from typing import List, Dict, Any, Optional


def analyze_co_gaps(co_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyzes CO attainment against targets.
    
    Each result in co_results should contain:
      - co_code: str (e.g., 'CO2')
      - co_description: str
      - target_attainment: float
      - actual_attainment: float
      - gap_percentage_points: float
      - severity: str ('ON_TARGET', 'MODERATE', 'HIGH', 'CRITICAL')
      - blooms_level: str
    """
    insights = []

    for co in co_results:
        gap = co.get("gap_percentage_points", 0.0)
        co_code = co.get("co_code", "Unknown CO")
        target = co.get("target_attainment", 70.0)
        actual = co.get("actual_attainment", 0.0)
        severity = co.get("severity", "ON_TARGET")
        blooms = co.get("blooms_level", "Apply")

        if gap > 0:
            impact_desc = (
                f"Students are falling short of expected competency in {co_code} "
                f"({blooms} cognitive level) by {gap:.1f} percentage points."
            )
            recommendation = (
                f"Conduct focused remedial tutorials, targeted problem-solving worksheets, "
                f"and diagnostic formative quizzes for {co_code} before the next assessment cycle."
            )
            
            insights.append({
                "category": "CO_GAP",
                "severity": severity,
                "title": f"Attainment Gap Detected in {co_code}",
                "co_code": co_code,
                "blooms_level": blooms,
                "target_attainment": target,
                "actual_attainment": actual,
                "gap_percentage_points": gap,
                "evidence": f"Target: {target}%, Measured Attainment: {actual}%, Gap: {gap:.1f} percentage points.",
                "rule_applied": f"Severity rule: Gap {gap:.1f} >= threshold for {severity}",
                "educational_impact": impact_desc,
                "recommended_action": recommendation,
            })

    return insights


def detect_weak_questions(
    question_stats: List[Dict[str, Any]],
    weakness_threshold_pct: float = 50.0
) -> List[Dict[str, Any]]:
    """
    Detects questions where student success rate is below weakness_threshold_pct.
    """
    weak_questions = []

    for q in question_stats:
        att = q.get("attainment_percentage", 0.0)
        q_num = q.get("question_number", "")
        max_marks = q.get("max_marks", 0.0)
        co_code = q.get("mapped_co_code", "")

        if att < weakness_threshold_pct:
            weak_questions.append({
                "category": "WEAK_QUESTION",
                "severity": "CRITICAL" if att < 35.0 else "HIGH",
                "title": f"High Failure Rate on Question {q_num}",
                "question_number": q_num,
                "mapped_co": co_code,
                "attainment_percentage": att,
                "evidence": f"Only {att:.1f}% of students met the passing threshold on question {q_num} (Max Marks: {max_marks}).",
                "rule_applied": f"Success rate ({att:.1f}%) < {weakness_threshold_pct}% threshold",
                "educational_impact": f"Indicates potential ambiguity in question framing or widespread student difficulty with mapped outcome {co_code}.",
                "recommended_action": f"Review question rubric and provide targeted practice on this topic in lecture/lab."
            })

    return weak_questions


def detect_component_disparities(
    component_attainments: Dict[str, float],
    disparity_threshold: float = 15.0
) -> List[Dict[str, Any]]:
    """
    Detects significant performance disparities between CIE (Continuous Internal Evaluation)
    and SEE (Semester End Exam).
    """
    insights = []
    cie_att = component_attainments.get("CIE")
    see_att = component_attainments.get("SEE")

    if cie_att is not None and see_att is not None:
        diff = abs(cie_att - see_att)
        if diff >= disparity_threshold:
            if cie_att > see_att:
                higher, lower = "CIE", "SEE"
            else:
                higher, lower = "SEE", "CIE"

            insights.append({
                "category": "COMPONENT_DISPARITY",
                "severity": "HIGH",
                "title": f"Evaluation Component Disparity: {higher} vs {lower}",
                "cie_attainment": cie_att,
                "see_attainment": see_att,
                "difference": round(diff, 2),
                "evidence": f"Internal {higher} attainment is {cie_att:.1f}%, while {lower} attainment is {see_att:.1f}% (disparity of {diff:.1f} points).",
                "rule_applied": f"Absolute delta ({diff:.1f} pts) >= threshold of {disparity_threshold} pts.",
                "educational_impact": "Substantial variation suggests potential grade inflation in internals or unexpected difficulty spikes in terminal exams.",
                "recommended_action": "Calibrate assessment question difficulty between internal tests and terminal examinations for constructive alignment."
            })

    return insights


def identify_at_risk_students(
    student_records: List[Dict[str, Any]],
    failing_co_threshold: int = 2
) -> List[Dict[str, Any]]:
    """
    Identifies students who fail to meet thresholds on multiple course outcomes.
    
    Each item in student_records:
      - student_id: int
      - usn: str
      - full_name: str
      - failed_cos: List[str]
      - average_score_pct: float
    """
    at_risk = []

    for s in student_records:
        failed = s.get("failed_cos", [])
        avg_score = s.get("average_score_pct", 0.0)

        if len(failed) >= failing_co_threshold or avg_score < 45.0:
            at_risk.append({
                "category": "AT_RISK_STUDENT",
                "severity": "CRITICAL" if len(failed) >= 3 or avg_score < 35.0 else "HIGH",
                "title": f"Student Academic Support Needed: {s.get('usn')}",
                "student_id": s.get("student_id"),
                "usn": s.get("usn"),
                "full_name": s.get("full_name"),
                "failed_cos_count": len(failed),
                "failed_cos": failed,
                "average_score_pct": avg_score,
                "evidence": f"Below passing threshold in {len(failed)} COs ({', '.join(failed)}) with overall average score of {avg_score:.1f}%.",
                "rule_applied": f"Failing >= {failing_co_threshold} COs or average score < 45%",
                "educational_impact": "High risk of failing the course and missing prerequisite readiness for subsequent coursework.",
                "recommended_action": "Schedule personalized academic counseling, assign peer tutors, and track improvement via remedial assignments."
            })

    return at_risk
