"""
Automated Tests for Spreadsheet Import Validation and Error Handling
"""

import pandas as pd
import pytest
from backend.app.services.import_service import validate_student_roster, validate_assessment_marks


def test_student_roster_validation_success():
    df = pd.DataFrame([
        {"USN": "1AP22CS101", "Full Name": "Test Student 1", "Email": "s1@apex.edu", "Batch": "2022-2026", "Semester": 5},
        {"USN": "1AP22CS102", "Full Name": "Test Student 2", "Email": "s2@apex.edu", "Batch": "2022-2026", "Semester": 5},
    ])
    valid_rows, error_rows = validate_student_roster(df)
    assert len(valid_rows) == 2
    assert len(error_rows) == 0


def test_student_roster_duplicate_usn():
    df = pd.DataFrame([
        {"USN": "1AP22CS101", "Full Name": "Student One"},
        {"USN": "1AP22CS101", "Full Name": "Duplicate USN Student"},
    ])
    valid_rows, error_rows = validate_student_roster(df)
    assert len(valid_rows) == 1
    assert len(error_rows) == 1
    assert "Duplicate USN" in error_rows[0]["message"]


def test_student_roster_empty_name():
    df = pd.DataFrame([
        {"USN": "1AP22CS103", "Full Name": ""},
    ])
    valid_rows, error_rows = validate_student_roster(df)
    assert len(valid_rows) == 0
    assert len(error_rows) == 1
    assert "name cannot be empty" in error_rows[0]["message"].lower()


def test_assessment_marks_validation_marks_exceed_max():
    questions = [
        {"id": 1, "question_number": "Q1a", "max_marks": 10.0},
    ]
    enrolled_usns = ["1AP22CS001"]
    
    # 15.0 marks on a 10.0 max marks question
    df = pd.DataFrame([
        {"USN": "1AP22CS001", "Q1a": 15.0},
    ])
    valid_marks, error_rows = validate_assessment_marks(df, questions, enrolled_usns)
    assert len(valid_marks) == 0
    assert len(error_rows) == 1
    assert "exceed maximum" in error_rows[0]["message"]


def test_assessment_marks_negative_marks():
    questions = [
        {"id": 1, "question_number": "Q1a", "max_marks": 10.0},
    ]
    enrolled_usns = ["1AP22CS001"]

    df = pd.DataFrame([
        {"USN": "1AP22CS001", "Q1a": -3.5},
    ])
    valid_marks, error_rows = validate_assessment_marks(df, questions, enrolled_usns)
    assert len(valid_marks) == 0
    assert len(error_rows) == 1
    assert "cannot be negative" in error_rows[0]["message"]


def test_assessment_marks_absent_codes():
    questions = [
        {"id": 1, "question_number": "Q1a", "max_marks": 10.0},
    ]
    enrolled_usns = ["1AP22CS001", "1AP22CS002"]

    df = pd.DataFrame([
        {"USN": "1AP22CS001", "Q1a": "AB"},
        {"USN": "1AP22CS002", "Q1a": 8.5},
    ])
    valid_marks, error_rows = validate_assessment_marks(df, questions, enrolled_usns)
    assert len(error_rows) == 0
    assert len(valid_marks) == 2
    # Student 1 is absent
    s1 = next(m for m in valid_marks if m["usn"] == "1AP22CS001")
    assert s1["is_absent"] is True
    assert s1["marks_obtained"] is None
    # Student 2 has marks
    s2 = next(m for m in valid_marks if m["usn"] == "1AP22CS002")
    assert s2["is_absent"] is False
    assert s2["marks_obtained"] == 8.5
