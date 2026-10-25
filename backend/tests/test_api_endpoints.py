"""
Automated Backend Tests for Core Academic and Analytics API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def get_faculty_token():
    res = client.post("/api/auth/login-json", json={
        "email": "sarah.jenkins@apex.edu",
        "password": "Faculty@12345"
    })
    return res.json()["access_token"]


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_readiness_check():
    res = client.get("/readiness")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"


def test_list_institutions_and_courses():
    res = client.get("/api/academic/institutions")
    assert res.status_code == 200
    institutions = res.json()
    assert len(institutions) >= 1
    assert institutions[0]["code"] == "AIT"

    res_courses = client.get("/api/academic/courses")
    assert res_courses.status_code == 200
    courses = res_courses.json()
    assert any(c["code"] == "CS501" for c in courses)


def test_dashboard_metrics():
    res = client.get("/api/dashboard/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert "charts" in data
    assert data["kpis"]["total_active_courses"] >= 2
    assert data["kpis"]["total_enrolled_students"] >= 30
    assert data["kpis"]["cos_evaluated"] >= 4
    # Check that severity distribution chart has numbers
    assert any(item["name"] == "On Target" for item in data["charts"]["severity_distribution"])


def test_attainment_calculation_run():
    token = get_faculty_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Run calculation on offering 1
    res = client.post(
        "/api/attainment/run",
        json={"course_offering_id": 1, "summary_notes": "Automated test calculation"},
        headers=headers,
    )
    assert res.status_code == 200
    run_data = res.json()
    assert run_data["status"] == "COMPLETED"
    assert len(run_data["co_results"]) >= 4

    # Verify CO attainment result properties
    co1_res = next((c for c in run_data["co_results"] if c["co_code"] == "CO1"), None)
    assert co1_res is not None
    assert co1_res["target_attainment"] == 70.0
    assert co1_res["overall_attainment"] > 60.0
    assert co1_res["attainment_level"] in [1, 2, 3]


def test_gap_detection_analysis():
    res = client.get("/api/gaps/offerings/1/analysis")
    assert res.status_code == 200
    gap_data = res.json()
    assert gap_data["has_data"] is True
    assert "co_gaps" in gap_data
    # Should detect underperforming COs (e.g. CO2, CO3)
    assert len(gap_data["co_gaps"]) >= 1
    gap_co = gap_data["co_gaps"][0]
    assert "evidence" in gap_co
    assert "rule_applied" in gap_co
    assert "educational_impact" in gap_co
    assert "recommended_action" in gap_co


def test_recommendations_endpoint():
    res = client.get("/api/recommendations/offerings/1")
    assert res.status_code == 200
    rec_data = res.json()
    assert rec_data["has_data"] is True
    assert len(rec_data["recommendations"]) >= 1
    first_rec = rec_data["recommendations"][0]
    assert "suggested_teaching_action" in first_rec
    assert "suggested_practice_activity" in first_rec
    assert "follow_up_assessment" in first_rec


def test_pdf_report_download():
    res = client.get("/api/reports/offerings/1/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000  # valid binary PDF


def test_excel_report_download():
    res = client.get("/api/reports/offerings/1/excel")
    assert res.status_code == 200
    assert "application/vnd.openxmlformats" in res.headers["content-type"]
    assert len(res.content) > 1000
