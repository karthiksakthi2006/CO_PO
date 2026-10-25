"""
Automated Backend Tests for Authentication and Role-Based Access Control (RBAC)
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_login_success():
    res = client.post("/api/auth/login-json", json={
        "email": "admin@apex.edu",
        "password": "Admin@12345"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "SUPER_ADMIN"
    assert data["email"] == "admin@apex.edu"


def test_login_invalid_password():
    res = client.post("/api/auth/login-json", json={
        "email": "admin@apex.edu",
        "password": "WrongPassword!99"
    })
    assert res.status_code == 401
    assert "Incorrect email or password" in res.json()["detail"]


def test_get_current_user_profile():
    # Login as faculty
    login_res = client.post("/api/auth/login-json", json={
        "email": "sarah.jenkins@apex.edu",
        "password": "Faculty@12345"
    })
    token = login_res.json()["access_token"]

    # Request profile
    profile_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    user_data = profile_res.json()
    assert user_data["email"] == "sarah.jenkins@apex.edu"
    assert user_data["role"] == "FACULTY"


def test_rbac_student_blocked_from_admin():
    # Login as student
    login_res = client.post("/api/auth/login-json", json={
        "email": "1ap22cs001@apex.edu",
        "password": "Student@12345"
    })
    token = login_res.json()["access_token"]

    # Student attempts to list users (requires admin / HOD)
    res = client.get("/api/users", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403
    assert "Access denied" in res.json()["detail"]


def test_rbac_student_blocked_from_academic_and_grading_operations():
    # Login as student
    login_res = client.post("/api/auth/login-json", json={
        "email": "1ap22cs001@apex.edu",
        "password": "Student@12345"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Student cannot create courses
    res = client.post("/api/academic/courses", json={"code": "CS999", "name": "Illegal", "credits": 4, "semester_number": 5, "department_id": 1}, headers=headers)
    assert res.status_code == 403

    # Student cannot create assessments
    res = client.post("/api/assessments/offerings/1", json={"course_offering_id": 1, "name": "Illegal Exam", "assessment_type": "CIE", "weight_percentage": 20, "max_marks": 25}, headers=headers)
    assert res.status_code == 403

    # Student cannot submit marks
    res = client.post("/api/assessments/1/marks/batch", json={"marks": []}, headers=headers)
    assert res.status_code == 403

    # Student cannot run attainment calculations
    res = client.post("/api/attainment/run", json={"course_offering_id": 1, "summary_notes": "hack"}, headers=headers)
    assert res.status_code == 403

    # Student cannot create interventions
    res = client.post("/api/interventions", json={"course_offering_id": 1, "course_outcome_id": 1, "gap_percentage_points": 5, "severity": "MODERATE", "root_cause_analysis": "test", "action_plan": "test", "pedagogical_tool": "test"}, headers=headers)
    assert res.status_code == 403

    # Student cannot read audit logs
    res = client.get("/api/audit/logs", headers=headers)
    assert res.status_code == 403


def test_unauthenticated_request_rejected():
    res = client.get("/api/auth/me")
    assert res.status_code == 401
