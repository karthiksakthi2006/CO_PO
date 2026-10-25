"""
CO-ATTAIN PRO AI - Academic Report Generation Service
Generates NBA/NAAC compliant Course Outcome Attainment Reports in PDF and Excel format.
"""

import io
from datetime import datetime, timezone
from typing import Dict, Any, List
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_attainment_pdf_report(
    course_data: Dict[str, Any],
    co_results: List[Dict[str, Any]],
    po_results: List[Dict[str, Any]],
    gaps: List[Dict[str, Any]],
    interventions: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> bytes:
    """Generates an official NBA/NAAC Course Outcome Attainment Report in PDF format."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,  # Center
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )
    h2_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
    )
    cell_style = ParagraphStyle(
        "CellNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1e293b"),
    )
    cell_bold = ParagraphStyle(
        "CellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
    )

    # Document Header
    story.append(Paragraph("CO-ATTAIN PRO AI — OBE ACCREDITATION REPORT", title_style))
    story.append(Spacer(1, 4))
    inst_name = course_data.get("institution_name", "Apex Institute of Technology")
    dept_name = course_data.get("department_name", "Department of Computer Science & Engineering")
    story.append(Paragraph(f"{inst_name} — {dept_name}", subtitle_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3b82f6"), spaceAfter=12))

    # Academic Context Metadata Table
    meta_data = [
        [
            Paragraph("<b>Course Code:</b>", cell_bold),
            Paragraph(course_data.get("course_code", "CS501"), cell_style),
            Paragraph("<b>Course Name:</b>", cell_bold),
            Paragraph(course_data.get("course_name", "Database Management Systems"), cell_style),
        ],
        [
            Paragraph("<b>Academic Year:</b>", cell_bold),
            Paragraph(course_data.get("academic_year", "2024-2025"), cell_style),
            Paragraph("<b>Semester / Section:</b>", cell_bold),
            Paragraph(f"{course_data.get('semester_name', 'Semester 5')} (Sec {course_data.get('section', 'A')})", cell_style),
        ],
        [
            Paragraph("<b>Faculty In-Charge:</b>", cell_bold),
            Paragraph(course_data.get("faculty_name", "Dr. Sarah Jenkins"), cell_style),
            Paragraph("<b>Report Date:</b>", cell_bold),
            Paragraph(datetime.now(timezone.utc).strftime("%d %b %Y"), cell_style),
        ],
        [
            Paragraph("<b>Direct Method:</b>", cell_bold),
            Paragraph(f"{config.get('direct_method', 'THRESHOLD')} (Threshold: {config.get('threshold_percentage', 60.0)}%)", cell_style),
            Paragraph("<b>Weights:</b>", cell_bold),
            Paragraph(f"Direct: {config.get('direct_weight', 80.0)}% | Indirect: {config.get('indirect_weight', 20.0)}%", cell_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[100, 170, 110, 160])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # Section 1: Course Outcome Attainment Summary Table
    story.append(Paragraph("1. Course Outcome Attainment & Gap Analysis", h2_style))
    co_headers = [
        Paragraph("<b>CO Code</b>", cell_bold),
        Paragraph("<b>Bloom's Level</b>", cell_bold),
        Paragraph("<b>Target (%)</b>", cell_bold),
        Paragraph("<b>Direct (%)</b>", cell_bold),
        Paragraph("<b>Indirect (%)</b>", cell_bold),
        Paragraph("<b>Overall (%)</b>", cell_bold),
        Paragraph("<b>Level</b>", cell_bold),
        Paragraph("<b>Gap (pts)</b>", cell_bold),
        Paragraph("<b>Status</b>", cell_bold),
    ]
    table_co_data = [co_headers]

    for co in co_results:
        gap = co.get("gap_percentage_points", 0.0)
        gap_display = f"+{gap:.1f}" if gap > 0 else f"{gap:.1f}"
        sev = co.get("severity", "ON_TARGET")
        
        status_text = "On Target" if sev == "ON_TARGET" else sev.capitalize()

        table_co_data.append([
            Paragraph(f"<b>{co.get('co_code', 'CO')}</b>", cell_style),
            Paragraph(co.get("blooms_level", "Apply"), cell_style),
            Paragraph(f"{co.get('target_attainment', 70.0):.1f}%", cell_style),
            Paragraph(f"{co.get('direct_attainment', 0.0):.1f}%", cell_style),
            Paragraph(f"{co.get('indirect_attainment', 0.0):.1f}%" if co.get('indirect_attainment') else "N/A", cell_style),
            Paragraph(f"<b>{co.get('overall_attainment', 0.0):.1f}%</b>", cell_style),
            Paragraph(f"Level {co.get('attainment_level', 1)}", cell_style),
            Paragraph(gap_display, cell_style),
            Paragraph(status_text, cell_style),
        ])

    t_co = Table(table_co_data, colWidths=[55, 65, 55, 55, 60, 60, 50, 65, 75])
    t_co.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_co)
    story.append(Spacer(1, 14))

    # Section 2: Program Outcome (PO/PSO) Attainment
    if po_results:
        story.append(Paragraph("2. Program Outcome (PO/PSO) Contribution & Attainment", h2_style))
        po_headers = [
            Paragraph("<b>Outcome</b>", cell_bold),
            Paragraph("<b>Calculated Attainment (%)</b>", cell_bold),
            Paragraph("<b>Avg Mapping Strength (1-3)</b>", cell_bold),
            Paragraph("<b>Mapped CO Count</b>", cell_bold),
        ]
        table_po_data = [po_headers]
        for po in po_results:
            table_po_data.append([
                Paragraph(f"<b>{po.get('outcome_code', 'PO')}</b>", cell_style),
                Paragraph(f"{po.get('calculated_attainment', 0.0):.1f}%", cell_style),
                Paragraph(f"{po.get('average_strength', 0.0):.2f}", cell_style),
                Paragraph(str(po.get("mapped_co_count", 0)), cell_style),
            ])
        t_po = Table(table_po_data, colWidths=[100, 160, 160, 120])
        t_po.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_po)
        story.append(Spacer(1, 14))

    # Section 3: Remedial Interventions & Continuous Quality Improvement (CQI)
    if interventions:
        story.append(Paragraph("3. Continuous Quality Improvement (CQI) & Remedial Actions", h2_style))
        int_headers = [
            Paragraph("<b>CO Code</b>", cell_bold),
            Paragraph("<b>Identified Gap</b>", cell_bold),
            Paragraph("<b>Root Cause & Action Plan</b>", cell_bold),
            Paragraph("<b>Pre -> Post Attainment</b>", cell_bold),
            Paragraph("<b>Improvement</b>", cell_bold),
            Paragraph("<b>Status</b>", cell_bold),
        ]
        table_int_data = [int_headers]
        for item in interventions:
            pre_val = item.get("pre_intervention_attainment", 0.0)
            post_val = item.get("post_intervention_attainment")
            post_display = f"{post_val:.1f}%" if post_val is not None else "Pending"
            imp = item.get("improvement_percentage_points")
            imp_display = f"+{imp:.1f} pts" if imp is not None else "--"

            action_desc = f"<b>Plan:</b> {item.get('action_plan', '')[:90]}..."
            table_int_data.append([
                Paragraph(item.get("co_code", "CO"), cell_style),
                Paragraph(f"{item.get('gap_percentage_points', 0.0):.1f} pts", cell_style),
                Paragraph(action_desc, cell_style),
                Paragraph(f"{pre_val:.1f}% → {post_display}", cell_style),
                Paragraph(imp_display, cell_style),
                Paragraph(item.get("status", "IDENTIFIED"), cell_style),
            ])
        t_int = Table(table_int_data, colWidths=[55, 65, 185, 95, 65, 75])
        t_int.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_int)

    # Sign-off block
    story.append(Spacer(1, 30))
    sign_data = [
        [
            Paragraph("____________________________<br/><b>Course Instructor / Faculty</b>", cell_style),
            Paragraph("____________________________<br/><b>Module Coordinator</b>", cell_style),
            Paragraph("____________________________<br/><b>Head of Department (HOD)</b>", cell_style),
        ]
    ]
    t_sign = Table(sign_data, colWidths=[180, 180, 180])
    t_sign.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t_sign)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_attainment_excel_report(
    course_data: Dict[str, Any],
    co_results: List[Dict[str, Any]],
    po_results: List[Dict[str, Any]]
) -> bytes:
    """Generates an Excel workbook with Course Outcome and Program Outcome attainment sheets."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Sheet 1: Course Outcomes
        df_co = pd.DataFrame([
            {
                "CO Code": co.get("co_code"),
                "Bloom's Level": co.get("blooms_level"),
                "Target Attainment (%)": co.get("target_attainment"),
                "Direct Attainment (%)": co.get("direct_attainment"),
                "Indirect Attainment (%)": co.get("indirect_attainment"),
                "Overall Attainment (%)": co.get("overall_attainment"),
                "Attainment Level": co.get("attainment_level"),
                "Gap (pts)": co.get("gap_percentage_points"),
                "Severity": co.get("severity"),
            }
            for co in co_results
        ])
        df_co.to_excel(writer, sheet_name="CO Attainment", index=False)

        # Sheet 2: Program Outcomes
        if po_results:
            df_po = pd.DataFrame([
                {
                    "Outcome Code": po.get("outcome_code"),
                    "Calculated Attainment (%)": po.get("calculated_attainment"),
                    "Avg Mapping Strength": po.get("average_strength"),
                    "Mapped CO Count": po.get("mapped_co_count"),
                }
                for po in po_results
            ])
            df_po.to_excel(writer, sheet_name="PO-PSO Attainment", index=False)

    output.seek(0)
    return output.getvalue()
