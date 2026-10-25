"""
Deterministic Demo Data Seeder for CO-ATTAIN PRO AI
Populates complete academic context, students, assessments, marks, calculation runs,
gap detection insights, and Continuous Quality Improvement (CQI) interventions.
Usage:
  python -m backend.app.cli.seed
"""

import json
from datetime import datetime, timedelta, timezone
from backend.app.database import SessionLocal, Base, engine
import backend.app.models
from backend.app.models.auth import User, UserRole
from backend.app.models.academic import (
    Institution,
    Department,
    AcademicYear,
    Semester,
    Program,
    Course,
    CourseOffering,
    Student,
    Enrollment,
    CourseOutcome,
    ProgramOutcome,
    ProgramSpecificOutcome,
    CoPoMapping,
)
from backend.app.models.assessment import (
    AssessmentType,
    Assessment,
    Question,
    QuestionCoMapping,
    StudentMark,
    IndirectAssessment,
)
from backend.app.models.attainment import (
    DirectAttainmentMethod,
    MissingMarkPolicy,
    AttainmentSeverity,
    AttainmentConfiguration,
    AttainmentRun,
    CoAttainmentResult,
    PoAttainmentResult,
)
from backend.app.models.intervention import (
    InterventionStatus,
    EffectivenessRating,
    Intervention,
    Reassessment,
)
from backend.app.models.audit import AuditLog, ImportJob, Notification
from backend.app.services.auth_service import hash_password


def seed_data():
    print("[SEED] Resetting database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[SEED] Creating Institution & Department...")
    inst = Institution(
        code="AIT",
        name="Apex Institute of Technology",
        address="Campus Road, Tech District, City",
        contact_email="info@apex.edu",
    )
    db.add(inst)
    db.flush()

    dept = Department(
        institution_id=inst.id,
        code="CSE",
        name="Department of Computer Science & Engineering",
        head_name="Dr. Robert Vance",
    )
    db.add(dept)
    db.flush()

    print("[SEED] Creating Academic Users...")
    admin_user = User(
        email="admin@apex.edu",
        hashed_password=hash_password("Admin@12345"),
        full_name="System Administrator",
        role=UserRole.SUPER_ADMIN,
        institution_id=inst.id,
        department_id=dept.id,
        is_active=True,
    )
    hod_user = User(
        email="hod.cse@apex.edu",
        hashed_password=hash_password("Hod@12345"),
        full_name="Dr. Robert Vance (HOD)",
        role=UserRole.HOD,
        institution_id=inst.id,
        department_id=dept.id,
        is_active=True,
    )
    faculty_user = User(
        email="sarah.jenkins@apex.edu",
        hashed_password=hash_password("Faculty@12345"),
        full_name="Dr. Sarah Jenkins",
        role=UserRole.FACULTY,
        institution_id=inst.id,
        department_id=dept.id,
        is_active=True,
    )
    student_user = User(
        email="1ap22cs001@apex.edu",
        hashed_password=hash_password("Student@12345"),
        full_name="Aarav Sharma",
        role=UserRole.STUDENT,
        institution_id=inst.id,
        department_id=dept.id,
        is_active=True,
    )
    db.add_all([admin_user, hod_user, faculty_user, student_user])
    db.flush()

    print("[SEED] Creating Academic Calendar...")
    ay = AcademicYear(name="2024-2025", is_current=True)
    db.add(ay)
    db.flush()

    sem = Semester(
        academic_year_id=ay.id,
        name="Semester 5 (Fall 2024)",
        semester_number=5,
        is_active=True,
    )
    db.add(sem)
    db.flush()

    print("[SEED] Creating Program & Program Outcomes...")
    prog = Program(
        department_id=dept.id,
        code="BTECH-CSE",
        name="B.Tech Computer Science & Engineering",
        degree="B.Tech",
        total_credits=160,
    )
    db.add(prog)
    db.flush()

    po_definitions = [
        ("PO1", "Engineering Knowledge", "Apply knowledge of mathematics, science, engineering fundamentals to solve complex problems."),
        ("PO2", "Problem Analysis", "Identify, formulate, review research literature, and analyze complex engineering problems."),
        ("PO3", "Design/Development of Solutions", "Design solutions for complex engineering problems and design system components or processes."),
        ("PO4", "Conduct Investigations", "Use research-based knowledge and research methods including design of experiments."),
        ("PO5", "Modern Tool Usage", "Create, select, and apply appropriate techniques, resources, and modern IT tools."),
        ("PO6", "The Engineer and Society", "Apply reasoning informed by contextual knowledge to assess societal, health, safety, and legal issues."),
        ("PO7", "Environment and Sustainability", "Understand the impact of professional engineering solutions in societal and environmental contexts."),
        ("PO8", "Ethics", "Apply ethical principles and commit to professional ethics and responsibilities."),
        ("PO9", "Individual and Team Work", "Function effectively as an individual, and as a member or leader in diverse teams."),
        ("PO10", "Communication", "Communicate effectively on complex engineering activities with the engineering community."),
        ("PO11", "Project Management and Finance", "Demonstrate knowledge and understanding of engineering and management principles."),
        ("PO12", "Life-long Learning", "Recognize the need for, and have the preparation and ability to engage in independent and life-long learning."),
    ]
    po_objs = {}
    for code, title, desc in po_definitions:
        p = ProgramOutcome(program_id=prog.id, code=code, title=title, description=desc)
        db.add(p)
        db.flush()
        po_objs[code] = p

    pso_definitions = [
        ("PSO1", "Enterprise Systems & Databases", "Design and architect enterprise-grade software systems and reliable database architectures."),
        ("PSO2", "Algorithmic & AI Solutions", "Develop intelligent algorithms, scalable data structures, and computational optimization pipelines."),
    ]
    pso_objs = {}
    for code, title, desc in pso_definitions:
        ps = ProgramSpecificOutcome(program_id=prog.id, code=code, title=title, description=desc)
        db.add(ps)
        db.flush()
        pso_objs[code] = ps

    print("[SEED] Creating Courses...")
    c1 = Course(
        department_id=dept.id,
        program_id=prog.id,
        code="CS501",
        name="Database Management Systems",
        credits=4,
        semester_number=5,
        description="Relational data models, SQL algebra, indexing, ACID transactions, and NoSQL databases.",
    )
    c2 = Course(
        department_id=dept.id,
        program_id=prog.id,
        code="CS502",
        name="Design & Analysis of Algorithms",
        credits=4,
        semester_number=5,
        description="Divide and conquer, dynamic programming, greedy methods, and NP-completeness.",
    )
    db.add_all([c1, c2])
    db.flush()

    # Offerings
    offering1 = CourseOffering(
        course_id=c1.id,
        academic_year_id=ay.id,
        semester_id=sem.id,
        section="A",
        faculty_id=faculty_user.id,
        is_active=True,
    )
    offering2 = CourseOffering(
        course_id=c2.id,
        academic_year_id=ay.id,
        semester_id=sem.id,
        section="A",
        faculty_id=faculty_user.id,
        is_active=True,
    )
    db.add_all([offering1, offering2])
    db.flush()

    print("[SEED] Creating Course Outcomes for CS501...")
    co1 = CourseOutcome(
        course_id=c1.id,
        code="CO1",
        description="Understand relational database concepts, ER modeling, and relational algebra.",
        blooms_level="Understand",
        target_attainment_percentage=70.0,
    )
    co2 = CourseOutcome(
        course_id=c1.id,
        code="CO2",
        description="Apply SQL queries, subqueries, views, and integrity constraints in relational schemas.",
        blooms_level="Apply",
        target_attainment_percentage=70.0,
    )
    co3 = CourseOutcome(
        course_id=c1.id,
        code="CO3",
        description="Analyze database normalization, B+ tree indexing structures, and transaction concurrency protocols.",
        blooms_level="Analyze",
        target_attainment_percentage=70.0,
    )
    co4 = CourseOutcome(
        course_id=c1.id,
        code="CO4",
        description="Design and architect distributed data pipelines and NoSQL document storage.",
        blooms_level="Create",
        target_attainment_percentage=70.0,
    )
    db.add_all([co1, co2, co3, co4])
    db.flush()

    print("[SEED] Creating CO-PO Mappings...")
    mappings_data = [
        # (CO, PO_code, strength, justification)
        (co1, "PO1", 3, "Direct application of foundational database theory."),
        (co1, "PO2", 2, "Problem analysis in conceptual data modeling."),
        (co2, "PO1", 2, "SQL syntax and mathematical relation queries."),
        (co2, "PO3", 3, "Design of queries for enterprise reporting systems."),
        (co2, "PO5", 2, "Use of PostgreSQL and modern DB management tools."),
        (co3, "PO2", 3, "Rigorous analysis of functional dependencies and normal forms."),
        (co3, "PO3", 2, "Indexing design to mitigate query latency."),
        (co4, "PO3", 3, "End-to-end design of distributed NoSQL data stores."),
        (co4, "PO5", 3, "Modern tools: Redis, MongoDB, and Cassandra integration."),
    ]
    for co_ref, po_code, strength, just in mappings_data:
        m = CoPoMapping(
            course_outcome_id=co_ref.id,
            program_outcome_id=po_objs[po_code].id,
            mapping_strength=strength,
            justification=just,
        )
        db.add(m)

    # PSO mappings
    db.add(CoPoMapping(course_outcome_id=co1.id, program_specific_outcome_id=pso_objs["PSO1"].id, mapping_strength=3, justification="Core database models"))
    db.add(CoPoMapping(course_outcome_id=co2.id, program_specific_outcome_id=pso_objs["PSO1"].id, mapping_strength=3, justification="Enterprise SQL implementations"))
    db.add(CoPoMapping(course_outcome_id=co3.id, program_specific_outcome_id=pso_objs["PSO1"].id, mapping_strength=2, justification="Indexing architecture"))
    db.add(CoPoMapping(course_outcome_id=co4.id, program_specific_outcome_id=pso_objs["PSO2"].id, mapping_strength=2, justification="Distributed architecture"))
    db.flush()

    print("[SEED] Creating 30 Student Records and Enrollments...")
    names = [
        "Aarav Sharma", "Ananya Patel", "Bhavya Reddy", "Chirag Verma", "Divya Nair",
        "Eshaan Gupta", "Farhan Khan", "Gayatri Joshi", "Harish Kumar", "Ishita Roy",
        "Jatin Das", "Kavya Menon", "Lakshya Singh", "Meera Pillai", "Nikhil Rao",
        "Ojaswi Sen", "Pranav Deshmukh", "Pooja Hegde", "Rahul Venkatesh", "Riya Mukherjee",
        "Siddharth Bhatt", "Sneha Kulkarni", "Tarun Chawla", "Uma Maheshwari", "Varun Chopra",
        "Vidya Iyer", "Yashwant Prasad", "Zoya Sheikh", "Karthik Raja", "Lavanya Sundaram"
    ]

    students = []
    for i, name in enumerate(names, 1):
        usn = f"1AP22CS{i:03d}"
        s = Student(
            institution_id=inst.id,
            department_id=dept.id,
            usn=usn,
            full_name=name,
            email=f"{usn.lower()}@apex.edu",
            batch_year="2022-2026",
            current_semester=5,
            is_active=True,
        )
        db.add(s)
        students.append(s)
    db.flush()

    # Link first student to student_user
    student_user.student_id = students[0].id

    # Enroll in CS501
    for s in students:
        db.add(Enrollment(course_offering_id=offering1.id, student_id=s.id))
    db.flush()

    print("[SEED] Creating Assessments & Questions...")
    # Assessment 1: CIE 1 (Max 30) - Tests CO1 & CO2
    cie1 = Assessment(
        course_offering_id=offering1.id,
        name="Internal Assessment 1 (CIE 1)",
        assessment_type=AssessmentType.CIE,
        weight_percentage=25.0,
        max_marks=30.0,
        conduct_date=datetime.now(timezone.utc) - timedelta(days=45),
    )
    # Assessment 2: CIE 2 (Max 30) - Tests CO2 & CO3
    cie2 = Assessment(
        course_offering_id=offering1.id,
        name="Internal Assessment 2 (CIE 2)",
        assessment_type=AssessmentType.CIE,
        weight_percentage=25.0,
        max_marks=30.0,
        conduct_date=datetime.now(timezone.utc) - timedelta(days=20),
    )
    # Assessment 3: SEE (Max 100) - Tests CO1, CO2, CO3
    see = Assessment(
        course_offering_id=offering1.id,
        name="Semester End Examination (SEE)",
        assessment_type=AssessmentType.SEE,
        weight_percentage=50.0,
        max_marks=100.0,
        conduct_date=datetime.now(timezone.utc) - timedelta(days=5),
    )
    db.add_all([cie1, cie2, see])
    db.flush()

    # Questions for CIE 1
    q1_1 = Question(assessment_id=cie1.id, question_number="Q1a", max_marks=10.0, description="ER Diagram modeling")
    q1_2 = Question(assessment_id=cie1.id, question_number="Q1b", max_marks=10.0, description="Relational algebra expressions")
    q1_3 = Question(assessment_id=cie1.id, question_number="Q2", max_marks=10.0, description="SQL nested queries and views")
    db.add_all([q1_1, q1_2, q1_3])
    db.flush()

    db.add(QuestionCoMapping(question_id=q1_1.id, course_outcome_id=co1.id, weight=1.0))
    db.add(QuestionCoMapping(question_id=q1_2.id, course_outcome_id=co1.id, weight=1.0))
    db.add(QuestionCoMapping(question_id=q1_3.id, course_outcome_id=co2.id, weight=1.0))

    # Questions for CIE 2
    q2_1 = Question(assessment_id=cie2.id, question_number="Q1", max_marks=10.0, description="Complex SQL joins and aggregates")
    q2_2 = Question(assessment_id=cie2.id, question_number="Q2a", max_marks=10.0, description="3NF and BCNF normalization algorithms")
    q2_3 = Question(assessment_id=cie2.id, question_number="Q2b", max_marks=10.0, description="Concurrency control and deadlocks")
    db.add_all([q2_1, q2_2, q2_3])
    db.flush()

    db.add(QuestionCoMapping(question_id=q2_1.id, course_outcome_id=co2.id, weight=1.0))
    db.add(QuestionCoMapping(question_id=q2_2.id, course_outcome_id=co3.id, weight=1.0))
    db.add(QuestionCoMapping(question_id=q2_3.id, course_outcome_id=co3.id, weight=1.0))

    # Questions for SEE
    q3_1 = Question(assessment_id=see.id, question_number="Q1", max_marks=20.0, description="Relational data algebra (CO1)")
    q3_2 = Question(assessment_id=see.id, question_number="Q2", max_marks=30.0, description="Advanced SQL & Transaction Processing (CO2)")
    q3_3 = Question(assessment_id=see.id, question_number="Q3", max_marks=50.0, description="B+ Tree indexing & Normalization decomposition (CO3)")
    db.add_all([q3_1, q3_2, q3_3])
    db.flush()

    db.add(QuestionCoMapping(question_id=q3_1.id, course_outcome_id=co1.id, weight=1.0))
    db.add(QuestionCoMapping(question_id=q3_2.id, course_outcome_id=co2.id, weight=1.0))
    db.add(QuestionCoMapping(question_id=q3_3.id, course_outcome_id=co3.id, weight=1.0))

    # Indirect Exit Survey
    db.add(IndirectAssessment(
        course_offering_id=offering1.id,
        course_outcome_id=co1.id,
        survey_name="Course Exit Survey",
        total_responses=30,
        average_score=4.2,
        max_possible_score=5.0,
        attainment_percentage=84.0,
    ))
    db.add(IndirectAssessment(
        course_offering_id=offering1.id,
        course_outcome_id=co2.id,
        survey_name="Course Exit Survey",
        total_responses=30,
        average_score=3.6,
        max_possible_score=5.0,
        attainment_percentage=72.0,
    ))
    db.add(IndirectAssessment(
        course_offering_id=offering1.id,
        course_outcome_id=co3.id,
        survey_name="Course Exit Survey",
        total_responses=30,
        average_score=2.8,
        max_possible_score=5.0,
        attainment_percentage=56.0,
    ))

    print("[SEED] Generating Marks for 30 Students...")
    # Intentionally crafted deterministic scores to fulfill requirements:
    # CO1: High attainment (~78%) -> Meets target (70%)
    # CO2: Moderate attainment (~64%) -> Slightly below target (70%), gap ~6 pts (MODERATE)
    # CO3: Critical attainment (~46%) -> Significant gap ~24 pts (CRITICAL)
    # CO4: No questions mapped yet -> INSUFFICIENT DATA
    import random
    random.seed(42)

    all_questions = [
        (q1_1, 10.0, 0.82), # CO1
        (q1_2, 10.0, 0.78), # CO1
        (q1_3, 10.0, 0.65), # CO2
        (q2_1, 10.0, 0.63), # CO2
        (q2_2, 10.0, 0.44), # CO3
        (q2_3, 10.0, 0.48), # CO3
        (q3_1, 20.0, 0.76), # CO1
        (q3_2, 30.0, 0.64), # CO2
        (q3_3, 50.0, 0.45), # CO3
    ]

    for q_obj, max_m, mean_factor in all_questions:
        for idx, s in enumerate(students):
            # One student absent occasionally
            is_absent = (idx == 28 and q_obj.assessment_id == cie1.id)
            if is_absent:
                mark = None
            else:
                variation = ((idx * 7 + 13) % 21 - 10) / 100.0  # -0.10 to +0.10 deterministic
                score = round(max(0.0, min(max_m, max_m * (mean_factor + variation))), 1)
                mark = score

            db.add(StudentMark(
                assessment_id=q_obj.assessment_id,
                question_id=q_obj.id,
                student_id=s.id,
                marks_obtained=mark,
                is_absent=is_absent,
            ))
    db.flush()

    print("[SEED] Creating Attainment Configuration & Running Attainment Calculation...")
    config = AttainmentConfiguration(
        course_offering_id=offering1.id,
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
    db.flush()

    # Pre-calculated AttainmentRun
    run = AttainmentRun(
        course_offering_id=offering1.id,
        configuration_id=config.id,
        run_timestamp=datetime.now(timezone.utc) - timedelta(days=2),
        method_used="THRESHOLD",
        status="COMPLETED",
        summary_notes="Initial baseline OBE attainment run for Semester 5 cohort.",
        run_by_user_id=faculty_user.id,
    )
    db.add(run)
    db.flush()

    # CO Results
    # CO1: Direct 76.7%, Indirect 84.0% -> Overall 78.2% (Target 70%, Gap -8.2, ON_TARGET, Level 3)
    co1_res = CoAttainmentResult(
        attainment_run_id=run.id,
        course_outcome_id=co1.id,
        direct_attainment=76.7,
        indirect_attainment=84.0,
        overall_attainment=78.2,
        target_attainment=70.0,
        attainment_level=3,
        gap_percentage_points=-8.2,
        severity=AttainmentSeverity.ON_TARGET,
        eligible_students_count=30,
        details_json=json.dumps({"summary": "CO1 target met cleanly with strong relational algebra comprehension."}),
    )
    # CO2: Direct 63.3%, Indirect 72.0% -> Overall 65.0% (Target 70%, Gap +5.0, MODERATE, Level 2)
    co2_res = CoAttainmentResult(
        attainment_run_id=run.id,
        course_outcome_id=co2.id,
        direct_attainment=63.3,
        indirect_attainment=72.0,
        overall_attainment=65.0,
        target_attainment=70.0,
        attainment_level=2,
        gap_percentage_points=5.0,
        severity=AttainmentSeverity.MODERATE,
        eligible_students_count=30,
        details_json=json.dumps({"summary": "CO2 slightly below target; students struggled with correlated subqueries."}),
    )
    # CO3: Direct 43.3%, Indirect 56.0% -> Overall 45.8% (Target 70%, Gap +24.2, CRITICAL, Level 1)
    co3_res = CoAttainmentResult(
        attainment_run_id=run.id,
        course_outcome_id=co3.id,
        direct_attainment=43.3,
        indirect_attainment=56.0,
        overall_attainment=45.8,
        target_attainment=70.0,
        attainment_level=1,
        gap_percentage_points=24.2,
        severity=AttainmentSeverity.CRITICAL,
        eligible_students_count=30,
        details_json=json.dumps({"summary": "Critical gap in BCNF decomposition and B+ Tree concurrency control."}),
    )
    # CO4: Insufficient data
    co4_res = CoAttainmentResult(
        attainment_run_id=run.id,
        course_outcome_id=co4.id,
        direct_attainment=0.0,
        indirect_attainment=None,
        overall_attainment=0.0,
        target_attainment=70.0,
        attainment_level=1,
        gap_percentage_points=70.0,
        severity=AttainmentSeverity.CRITICAL,
        eligible_students_count=0,
        details_json=json.dumps({"summary": "Insufficient data: Outcome not yet assessed in primary test cycle."}),
    )
    db.add_all([co1_res, co2_res, co3_res, co4_res])
    db.flush()

    # PO Results
    db.add(PoAttainmentResult(attainment_run_id=run.id, program_outcome_id=po_objs["PO1"].id, outcome_code="PO1", calculated_attainment=72.9, average_strength=2.5, mapped_co_count=2))
    db.add(PoAttainmentResult(attainment_run_id=run.id, program_outcome_id=po_objs["PO2"].id, outcome_code="PO2", calculated_attainment=58.8, average_strength=2.5, mapped_co_count=2))
    db.add(PoAttainmentResult(attainment_run_id=run.id, program_outcome_id=po_objs["PO3"].id, outcome_code="PO3", calculated_attainment=55.4, average_strength=2.5, mapped_co_count=2))
    db.add(PoAttainmentResult(attainment_run_id=run.id, program_outcome_id=po_objs["PO5"].id, outcome_code="PO5", calculated_attainment=65.0, average_strength=2.0, mapped_co_count=1))
    db.add(PoAttainmentResult(attainment_run_id=run.id, program_specific_outcome_id=pso_objs["PSO1"].id, outcome_code="PSO1", calculated_attainment=63.0, average_strength=2.67, mapped_co_count=3))
    db.flush()

    print("[SEED] Creating Completed CQI Remedial Intervention & Reassessment...")
    # Completed intervention for CO3 showing verified improvement
    intervention = Intervention(
        course_offering_id=offering1.id,
        course_outcome_id=co3.id,
        gap_percentage_points=24.2,
        severity=AttainmentSeverity.CRITICAL,
        root_cause_analysis="Students demonstrated conceptual gaps in multi-valued dependency loss testing and deadlock graph resolution.",
        action_plan="Conducted 3 targeted tutorial workshops on BCNF decomposition step-by-step algorithms and distributed 50 practice trace problems.",
        pedagogical_tool="Remedial Interactive Whiteboard Recitation & Guided Trace Worksheets",
        assigned_faculty_id=faculty_user.id,
        target_completion_date=datetime.now(timezone.utc) - timedelta(days=1),
        status=InterventionStatus.COMPLETED,
        pre_intervention_attainment=45.8,
        post_intervention_attainment=65.0,
        improvement_percentage_points=19.2,
        effectiveness_rating=EffectivenessRating.EFFECTIVE,
    )
    db.add(intervention)
    db.flush()

    reassessment = Reassessment(
        intervention_id=intervention.id,
        assessment_name="Post-Remedial Diagnostic Quiz & Trace Evaluation",
        conduct_date=datetime.now(timezone.utc) - timedelta(days=1),
        total_students=28,
        students_passed=21,
        average_score=15.6,
        reassessment_attainment=65.0,
        notes="21 out of 28 participating students achieved >= 60% in normal form decomposition questions, showing +19.2 points improvement.",
    )
    db.add(reassessment)
    db.flush()

    # Seed demonstration import jobs and audit logs
    job1 = ImportJob(
        user_id=faculty_user.id,
        import_type="ASSESSMENT_MARKS",
        file_name="CS501_CIE1_Marks_BatchA.xlsx",
        status="SUCCESS",
        total_rows=30,
        imported_rows=30,
        failed_rows=0,
        created_at=datetime.now(timezone.utc) - timedelta(days=40),
    )
    job2 = ImportJob(
        user_id=faculty_user.id,
        import_type="ASSESSMENT_MARKS",
        file_name="CS501_SEE_Marks_Terminal.csv",
        status="SUCCESS",
        total_rows=30,
        imported_rows=30,
        failed_rows=0,
        created_at=datetime.now(timezone.utc) - timedelta(days=5),
    )
    db.add_all([job1, job2])

    logs = [
        AuditLog(
            user_id=faculty_user.id,
            action="LOGIN",
            entity_type="User",
            entity_id=str(faculty_user.id),
            ip_address="127.0.0.1",
            details_json=json.dumps({"role": "FACULTY", "agent": "Chrome 131"}),
            created_at=datetime.now(timezone.utc) - timedelta(days=40, hours=2),
        ),
        AuditLog(
            user_id=faculty_user.id,
            action="IMPORT_MARKS",
            entity_type="Assessment",
            entity_id=str(cie1.id),
            ip_address="127.0.0.1",
            details_json=json.dumps({"rows": 30, "assessment": "Internal Assessment 1 (CIE 1)"}),
            created_at=datetime.now(timezone.utc) - timedelta(days=40),
        ),
        AuditLog(
            user_id=faculty_user.id,
            action="CALCULATE_ATTAINMENT",
            entity_type="CourseOffering",
            entity_id=str(offering1.id),
            ip_address="127.0.0.1",
            details_json=json.dumps({"method": "THRESHOLD", "run_id": run.id, "threshold_pct": 60.0}),
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
        ),
        AuditLog(
            user_id=faculty_user.id,
            action="CREATE_INTERVENTION",
            entity_type="CourseOutcome",
            entity_id=str(co3.id),
            ip_address="127.0.0.1",
            details_json=json.dumps({"co_code": "CO3", "gap_pts": 24.2, "tool": "Tutorials"}),
            created_at=datetime.now(timezone.utc) - timedelta(days=1, hours=4),
        ),
        AuditLog(
            user_id=faculty_user.id,
            action="RECORD_REASSESSMENT",
            entity_type="Intervention",
            entity_id=str(intervention.id),
            ip_address="127.0.0.1",
            details_json=json.dumps({"passed": 21, "total": 28, "improvement": 19.2}),
            created_at=datetime.now(timezone.utc) - timedelta(days=1),
        ),
    ]
    db.add_all(logs)

    db.commit()
    print("[SEED] Deterministic demo data successfully seeded!")
    print("----------------------------------------------------------------")
    print("User Credentials Available:")
    print("1. Super Admin: admin@apex.edu / Admin@12345")
    print("2. HOD:         hod.cse@apex.edu / Hod@12345")
    print("3. Faculty:     sarah.jenkins@apex.edu / Faculty@12345")
    print("4. Student:     1ap22cs001@apex.edu / Student@12345")
    print("----------------------------------------------------------------")
    db.close()


if __name__ == "__main__":
    seed_data()
