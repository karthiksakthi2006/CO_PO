"""
CO-ATTAIN PRO AI - Assessment Import & Data Validation Service
Handles CSV and Excel parsing, column mapping, row-level validation,
error reporting, and template generation.
"""

import io
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from backend.app.models.academic import Student
from backend.app.models.assessment import Question, StudentMark


def generate_student_roster_template() -> bytes:
    """Generates a downloadable CSV sample template for student roster import."""
    df = pd.DataFrame([
        {"USN": "1AP22CS001", "Full Name": "Aarav Sharma", "Email": "aarav.sharma@example.edu", "Batch": "2022-2026", "Semester": 5},
        {"USN": "1AP22CS002", "Full Name": "Ananya Patel", "Email": "ananya.patel@example.edu", "Batch": "2022-2026", "Semester": 5},
        {"USN": "1AP22CS003", "Full Name": "Bhavya Reddy", "Email": "bhavya.reddy@example.edu", "Batch": "2022-2026", "Semester": 5},
        {"USN": "1AP22CS004", "Full Name": "Chirag Verma", "Email": "chirag.verma@example.edu", "Batch": "2022-2026", "Semester": 5},
        {"USN": "1AP22CS005", "Full Name": "Divya Nair", "Email": "divya.nair@example.edu", "Batch": "2022-2026", "Semester": 5},
    ])
    return df.to_csv(index=False).encode("utf-8")


def generate_marks_import_template(questions: List[Dict[str, Any]]) -> bytes:
    """
    Generates a downloadable CSV sample template for assessment marks.
    Columns: USN, Student Name, followed by question numbers with max marks in header.
    """
    sample_row = {"USN": "1AP22CS001", "Student Name": "Aarav Sharma"}
    for q in questions:
        q_label = f"{q['question_number']} (Max {q['max_marks']})"
        sample_row[q_label] = round(q["max_marks"] * 0.8, 1)

    df = pd.DataFrame([sample_row])
    return df.to_csv(index=False).encode("utf-8")


def parse_spreadsheet_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Parses uploaded CSV or Excel file into a pandas DataFrame."""
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(file_bytes))
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        return pd.read_excel(io.BytesIO(file_bytes))
    else:
        raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")


def preview_spreadsheet(file_bytes: bytes, filename: str, max_rows: int = 5) -> Dict[str, Any]:
    """Generates preview of columns, data types, and first few rows."""
    df = parse_spreadsheet_file(file_bytes, filename)
    clean_cols = [str(col).strip() for col in df.columns]
    df.columns = clean_cols
    
    preview_rows = df.head(max_rows).fillna("").to_dict(orient="records")
    return {
        "columns": clean_cols,
        "total_rows": len(df),
        "preview_rows": preview_rows,
    }


def validate_student_roster(df: pd.DataFrame) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates student roster rows.
    Returns: (valid_rows, error_rows)
    """
    valid_rows = []
    error_rows = []
    seen_usns = set()

    col_map = {str(col).strip().upper(): col for col in df.columns}
    
    usn_col = col_map.get("USN") or col_map.get("ROLL NO") or col_map.get("REG_NO")
    name_col = col_map.get("FULL NAME") or col_map.get("NAME") or col_map.get("STUDENT NAME")
    email_col = col_map.get("EMAIL")
    batch_col = col_map.get("BATCH") or col_map.get("BATCH YEAR")
    sem_col = col_map.get("SEMESTER") or col_map.get("CURRENT SEMESTER")

    if not usn_col:
        raise ValueError("Missing required column: 'USN' or 'Roll No'.")
    if not name_col:
        raise ValueError("Missing required column: 'Full Name' or 'Student Name'.")

    for idx, row in df.iterrows():
        row_num = idx + 2  # 1-indexed header + 1
        raw_usn = str(row[usn_col]).strip() if pd.notna(row[usn_col]) else ""
        raw_name = str(row[name_col]).strip() if pd.notna(row[name_col]) else ""

        if not raw_usn or raw_usn.lower() == "nan":
            error_rows.append({"row": row_num, "usn": "", "field": "USN", "message": "USN cannot be empty."})
            continue

        if raw_usn in seen_usns:
            error_rows.append({"row": row_num, "usn": raw_usn, "field": "USN", "message": f"Duplicate USN '{raw_usn}' in file."})
            continue

        seen_usns.add(raw_usn)

        if not raw_name or raw_name.lower() == "nan":
            error_rows.append({"row": row_num, "usn": raw_usn, "field": "Full Name", "message": "Student name cannot be empty."})
            continue

        raw_email = str(row[email_col]).strip() if email_col and pd.notna(row[email_col]) else None
        raw_batch = str(row[batch_col]).strip() if batch_col and pd.notna(row[batch_col]) else "2022-2026"
        
        sem_val = 5
        if sem_col and pd.notna(row[sem_col]):
            try:
                sem_val = int(row[sem_col])
            except ValueError:
                sem_val = 5

        valid_rows.append({
            "usn": raw_usn,
            "full_name": raw_name,
            "email": raw_email,
            "batch_year": raw_batch,
            "current_semester": sem_val,
        })

    return valid_rows, error_rows


def validate_assessment_marks(
    df: pd.DataFrame,
    questions: List[Dict[str, Any]],  # list with 'id', 'question_number', 'max_marks'
    enrolled_usns: List[str]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Validates uploaded marks against registered questions and enrolled students.
    Returns: (valid_marks, error_rows)
    """
    valid_marks = []
    error_rows = []
    enrolled_set = set(enrolled_usns)

    # Clean columns
    col_map = {str(col).strip().upper(): col for col in df.columns}
    usn_col = col_map.get("USN") or col_map.get("ROLL NO") or col_map.get("REG_NO")
    if not usn_col:
        raise ValueError("Missing required student identifier column: 'USN'.")

    # Match question columns
    question_col_mapping = {}
    for q in questions:
        q_num = str(q["question_number"]).strip().upper()
        # Find matching column
        matched_col = None
        for col_name in df.columns:
            cleaned = str(col_name).strip().upper()
            if cleaned == q_num or cleaned.startswith(f"{q_num} ") or cleaned.startswith(f"{q_num}("):
                matched_col = col_name
                break
        if matched_col:
            question_col_mapping[q["id"]] = {
                "col_name": matched_col,
                "question_number": q["question_number"],
                "max_marks": q["max_marks"],
            }

    if not question_col_mapping:
        raise ValueError("No matching question columns found in spreadsheet. Ensure columns match question numbers (e.g., Q1a, Q1b, Q2).")

    for idx, row in df.iterrows():
        row_num = idx + 2
        raw_usn = str(row[usn_col]).strip() if pd.notna(row[usn_col]) else ""

        if not raw_usn or raw_usn.lower() == "nan":
            error_rows.append({"row": row_num, "usn": "", "field": "USN", "message": "USN is empty."})
            continue

        if enrolled_set and raw_usn not in enrolled_set:
            error_rows.append({
                "row": row_num,
                "usn": raw_usn,
                "field": "USN",
                "message": f"Student '{raw_usn}' is not enrolled in this course offering.",
            })
            continue

        for q_id, q_meta in question_col_mapping.items():
            val = row[q_meta["col_name"]]
            max_m = q_meta["max_marks"]
            q_num = q_meta["question_number"]

            is_absent = False
            mark_value = None

            if pd.isna(val) or str(val).strip().upper() in ["AB", "ABSENT", "NA", "A"]:
                is_absent = True
                mark_value = None
            else:
                try:
                    mark_float = float(val)
                    if mark_float < 0:
                        error_rows.append({
                            "row": row_num,
                            "usn": raw_usn,
                            "field": q_num,
                            "message": f"Marks cannot be negative ({mark_float}).",
                        })
                        continue
                    if mark_float > max_m:
                        error_rows.append({
                            "row": row_num,
                            "usn": raw_usn,
                            "field": q_num,
                            "message": f"Marks obtained ({mark_float}) exceed maximum question marks ({max_m}).",
                        })
                        continue
                    mark_value = mark_float
                except ValueError:
                    error_rows.append({
                        "row": row_num,
                        "usn": raw_usn,
                        "field": q_num,
                        "message": f"Invalid numeric mark value '{val}'.",
                    })
                    continue

            valid_marks.append({
                "usn": raw_usn,
                "question_id": q_id,
                "marks_obtained": mark_value,
                "is_absent": is_absent,
            })

    return valid_marks, error_rows
