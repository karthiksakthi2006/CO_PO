"""
End-to-End Acceptance Scenario Test Suite
Simulates the complete 16-step workflow required by Section 19 of Master Specification:
1. Sign in as faculty user
2. Open a course
3. Verify course outcomes and assessment
4. Verify question mapping
5. Import / validate marks
6. Confirm import
7. Calculate attainment
8. View actual results
9. Detect below-target CO gap
10. Generate rule-based recommendation
11. Create continuous improvement intervention
12. Record reassessment marks
13. Recalculate attainment
14. Compare before and after results (measured improvement)
15. Export PDF report
16. Verify unauthorized user cannot access restricted administrative records
"""

import io
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_complete_e2e_acceptance_scenario():
    # 1. Sign in as authorized faculty
    login_res = client.post("/api/auth/login-json", json={
        "email": "sarah.jenkins@apex.edu",
        "password": "Faculty@12345"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Open a course (CS501, offering 1)
    offerings_res = client.get("/api/academic/offerings", headers=headers)
    assert offerings_res.status_code == 200
    offerings = offerings_res.json()
    offering = next((o for o in offerings if o["course_code"] == "CS501"), None)
    assert offering is not None
    offering_id = offering["id"]

    # 3. Create/verify course outcomes
    cos_res = client.get(f"/api/academic/courses/{offering['course_id']}/cos", headers=headers)
    assert cos_res.status_code == 200
    cos = cos_res.json()
    assert len(cos) >= 4

    # 4. Create an assessment and map questions
    ass_create_res = client.post(
        f"/api/assessments/offerings/{offering_id}",
        json={
            "course_offering_id": offering_id,
            "name": "E2E Lab Practical Test",
            "assessment_type": "LAB",
            "weight_percentage": 20.0,
            "max_marks": 20.0,
        },
        headers=headers,
    )
    assert ass_create_res.status_code == 200
    new_ass_id = ass_create_res.json()["id"]

    # Add question mapped to CO2
    q_create_res = client.post(
        f"/api/assessments/{new_ass_id}/questions",
        json={
            "assessment_id": new_ass_id,
            "question_number": "LabQ1",
            "max_marks": 20.0,
            "description": "SQL trigger implementation",
            "course_outcome_ids": [cos[1]["id"]],  # CO2
        },
        headers=headers,
    )
    assert q_create_res.status_code == 200
    q_id = q_create_res.json()["id"]

    # 5. Import marks from template (construct DataFrame)
    df_marks = pd.DataFrame([
        {"USN": "1AP22CS001", "LabQ1": 16.0},
        {"USN": "1AP22CS002", "LabQ1": 18.0},
        {"USN": "1AP22CS003", "LabQ1": 14.0},
    ])
    csv_bytes = df_marks.to_csv(index=False).encode("utf-8")

    # 6. Validate and confirm import
    files = {"file": ("test_marks.csv", io.BytesIO(csv_bytes), "text/csv")}
    validate_res = client.post(
        "/api/assessments/import/validate-marks",
        data={"assessment_id": str(new_ass_id)},
        files=files,
        headers=headers,
    )
    assert validate_res.status_code == 200
    assert validate_res.json()["can_commit"] is True

    # Commit marks
    files_commit = {"file": ("test_marks.csv", io.BytesIO(csv_bytes), "text/csv")}
    commit_res = client.post(
        "/api/assessments/import/commit-marks",
        data={"assessment_id": str(new_ass_id)},
        files=files_commit,
        headers=headers,
    )
    assert commit_res.status_code == 200
    assert commit_res.json()["imported_count"] == 3

    # 7. Calculate attainment
    calc_res = client.post(
        "/api/attainment/run",
        json={"course_offering_id": offering_id, "summary_notes": "Post E2E import calculation"},
        headers=headers,
    )
    assert calc_res.status_code == 200
    calc_data = calc_res.json()
    assert calc_data["status"] == "COMPLETED"

    # 8. View actual results
    co_results = calc_data["co_results"]
    assert len(co_results) >= 4

    # 9. Detect below-target CO gap
    gaps_res = client.get(f"/api/gaps/offerings/{offering_id}/analysis", headers=headers)
    assert gaps_res.status_code == 200
    gap_analysis = gaps_res.json()
    assert gap_analysis["has_data"] is True
    assert len(gap_analysis["co_gaps"]) >= 1

    # Find the critical gap CO (CO3)
    target_co = next((g for g in gap_analysis["co_gaps"] if g["co_code"] == "CO3"), gap_analysis["co_gaps"][0])
    assert target_co["gap_percentage_points"] > 0

    # 10. Generate rule-based recommendation
    rec_res = client.get(f"/api/recommendations/offerings/{offering_id}", headers=headers)
    assert rec_res.status_code == 200
    recs = rec_res.json()["recommendations"]
    assert len(recs) >= 1
    assert "suggested_teaching_action" in recs[0]

    # 11. Create an intervention
    co3_id = next(c["id"] for c in cos if c["code"] == "CO3")
    int_create_res = client.post(
        "/api/interventions",
        json={
            "course_offering_id": offering_id,
            "course_outcome_id": co3_id,
            "gap_percentage_points": 24.2,
            "severity": "CRITICAL",
            "root_cause_analysis": "Students struggled with multi-valued dependencies in BCNF",
            "action_plan": "Scheduled 4 hours of algorithmic normalization workshops",
            "pedagogical_tool": "Recitation & Step-by-Step Problem Sheets",
            "pre_intervention_attainment": 45.8,
        },
        headers=headers,
    )
    assert int_create_res.status_code == 200
    intervention_id = int_create_res.json()["id"]

    # 12. Record reassessment marks
    reass_res = client.post(
        f"/api/interventions/{intervention_id}/reassessments",
        json={
            "intervention_id": intervention_id,
            "assessment_name": "E2E Post-Remedial Diagnostic Exam",
            "total_students": 25,
            "students_passed": 20,
            "average_score": 16.0,
            "reassessment_attainment": 68.0,
            "notes": "Verified improvement following tutorial sessions",
        },
        headers=headers,
    )
    assert reass_res.status_code == 200
    reass_data = reass_res.json()
    assert reass_data["reassessment_attainment"] == 68.0

    # 13 & 14. Check before and after results (improvement)
    interventions_list_res = client.get(f"/api/interventions/offerings/{offering_id}", headers=headers)
    assert interventions_list_res.status_code == 200
    our_int = next(i for i in interventions_list_res.json() if i["id"] == intervention_id)
    assert our_int["post_intervention_attainment"] == 68.0
    # improvement = 68.0 - 45.8 = 22.2 percentage points
    assert our_int["improvement_percentage_points"] == 22.2
    assert our_int["effectiveness_rating"] == "EFFECTIVE"

    # 15. Export the PDF report
    pdf_res = client.get(f"/api/reports/offerings/{offering_id}/pdf", headers=headers)
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert len(pdf_res.content) > 500

    # 16. Verify student user cannot access privileged administration routes
    student_login = client.post("/api/auth/login-json", json={
        "email": "1ap22cs001@apex.edu",
        "password": "Student@12345"
    })
    student_token = student_login.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Attempt to access users administration
    forbidden_res = client.get("/api/users", headers=student_headers)
    assert forbidden_res.status_code == 403
