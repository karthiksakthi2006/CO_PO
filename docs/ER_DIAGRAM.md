# Database Architecture & Entity Relationship Diagram

The **CO-ATTAIN PRO AI** database schema is designed for relational consistency, referential integrity, and accreditation auditability.

```mermaid
erDiagram
    INSTITUTIONS ||--o{ DEPARTMENTS : contains
    DEPARTMENTS ||--o{ PROGRAMS : offers
    DEPARTMENTS ||--o{ COURSES : owns
    DEPARTMENTS ||--o{ USERS : assigns
    DEPARTMENTS ||--o{ STUDENTS : enrolls
    PROGRAMS ||--o{ PROGRAM_OUTCOMES : defines
    PROGRAMS ||--o{ PROGRAM_SPECIFIC_OUTCOMES : defines
    ACADEMIC_YEARS ||--o{ SEMESTERS : schedules
    COURSES ||--o{ COURSE_OUTCOMES : defines
    COURSES ||--o{ COURSE_OFFERINGS : offers
    SEMESTERS ||--o{ COURSE_OFFERINGS : runs_in
    COURSE_OFFERINGS ||--o{ ENROLLMENTS : registers
    STUDENTS ||--o{ ENROLLMENTS : takes
    COURSE_OUTCOMES ||--o{ CO_PO_MAPPINGS : maps_to
    PROGRAM_OUTCOMES ||--o{ CO_PO_MAPPINGS : receives_mapping
    PROGRAM_SPECIFIC_OUTCOMES ||--o{ CO_PO_MAPPINGS : receives_pso_mapping
    COURSE_OFFERINGS ||--o{ ASSESSMENTS : conducts
    ASSESSMENTS ||--o{ QUESTIONS : contains
    QUESTIONS ||--o{ QUESTION_CO_MAPPINGS : aligns_to
    COURSE_OUTCOMES ||--o{ QUESTION_CO_MAPPINGS : maps_from
    STUDENTS ||--o{ STUDENT_MARKS : scores
    QUESTIONS ||--o{ STUDENT_MARKS : evaluates
    COURSE_OFFERINGS ||--o{ ATTAINMENT_CONFIGURATIONS : configures
    COURSE_OFFERINGS ||--o{ ATTAINMENT_RUNS : versions
    ATTAINMENT_RUNS ||--o{ CO_ATTAINMENT_RESULTS : records
    ATTAINMENT_RUNS ||--o{ PO_ATTAINMENT_RESULTS : records
    COURSE_OUTCOMES ||--o{ CO_ATTAINMENT_RESULTS : measured_in
    COURSE_OFFERINGS ||--o{ INTERVENTIONS : remediates
    COURSE_OUTCOMES ||--o{ INTERVENTIONS : targets
    INTERVENTIONS ||--o{ REASSESSMENTS : verifies
    USERS ||--o{ AUDIT_LOGS : performs
    USERS ||--o{ IMPORT_JOBS : executes
```

## Core Relational Tables

1. **`institutions`**: College/University root organization.
2. **`departments`**: Academic units (e.g. Computer Science & Engineering).
3. **`users`**: System accounts with Argon2 hashes and role-based permissions (`SUPER_ADMIN`, `HOD`, `FACULTY`, `STUDENT`).
4. **`academic_years` & `semesters`**: Temporal terms (e.g., 2024-2025, Semester 5).
5. **`programs`**: Degree programs (e.g., B.Tech CSE).
6. **`courses` & `course_offerings`**: Catalog courses and active section offerings.
7. **`students` & `enrollments`**: Registered cohorts and course registrations.
8. **`course_outcomes` (COs)**: Course competencies with Bloom's Taxonomy levels (Understand, Apply, Analyze, Create) and target percentages.
9. **`program_outcomes` (POs)** & **`program_specific_outcomes` (PSOs)**: Washington Accord PO1-PO12 and department-specific PSOs.
10. **`co_po_mappings`**: Mapping strength (0=None, 1=Low, 2=Medium, 3=High) and justification.
11. **`assessments` & `questions`**: CIE/SEE exams and individual questions with maximum marks.
12. **`question_co_mappings`**: Direct constructive alignment from exam questions to COs.
13. **`student_marks`**: Validated marks obtained, absence flags, and remarks.
14. **`attainment_configurations`**: Method A (Threshold) vs Method B (Normalized), thresholds, and direct/indirect weights.
15. **`attainment_runs` & `co_attainment_results`**: Immutable, versioned calculation snapshots recording direct, indirect, overall attainment, gaps, and severity.
16. **`po_attainment_results`**: Aggregated program-level attainment derived from CO mapping matrix.
17. **`interventions` & `reassessments`**: Closed-loop Continuous Quality Improvement (CQI) tracking and post-remedial verified improvement.
