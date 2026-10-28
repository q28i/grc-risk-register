"""
Academic University Project Report Generator: GRC_Risk_Register_Project_Report.pdf
Structured exactly according to Silver Oak University / MCA Project Report standards (28 pages total).
Student: Tanvi Mishra
Enrollment No: 2504070300016
Project: Cybersecurity Risk Management System (GRC Risk Register)

Includes:
- Natural, technical, humanized prose grounded directly in the codebase (Zero corporate/AI stock phrases)
- Authentic academic front matter (Cover, Certificate, Declaration, Acknowledgment, Abstract, TOC, LOF, LOT, LOA)
- Detailed Chapters 1 to 7 aligned with actual SQLite schemas, Python 3 Standard Library HTTP server, PBKDF2 hashing, and 33 unit tests
- Appendix A-D Evaluation Sheets with structured university marking rubrics and signed examiner placeholders
- Publication / Patent output page
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter

# Academic Palette
CLR_PRIMARY = colors.HexColor('#990000')      # Crimson Red
CLR_HEADER_LINE = colors.HexColor('#333333')
CLR_TEXT_PRI = colors.HexColor('#111111')
CLR_BG_LIGHT = colors.HexColor('#F8F9FA')
CLR_BORDER = colors.HexColor('#D0D0D0')
CLR_BORDER_DARK = colors.HexColor('#444444')

STUDENT_NAME = "Tanvi Mishra"
ENROLLMENT_NO = "2504070300016"


class AcademicNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for precise page numbering matching the Silver Oak University sample:
    - Page 1: Cover (No header, no footer, no page number)
    - Pages 2-10: Roman numerals (ii, iii, iv, v, vi, vii, viii, ix, x) centered at bottom
    - Pages 11-28: Arabic numerals (1, 2, 3... 18) centered in footer with top running header line:
        Running Header: "Cybersecurity Risk Management System" centered with horizontal rule
        Running Footer: Top line, centered page number, "Silver Oak College of Computer Application" at bottom
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, total_pages):
        page_num = self._pageNumber

        # Page 1: Cover Page
        if page_num == 1:
            return

        self.saveState()

        # Preliminary pages (Pages 2 to 10)
        roman_map = {
            2: "ii", 3: "iii", 4: "iv", 5: "v",
            6: "vi", 7: "vii", 8: "viii", 9: "ix", 10: "x"
        }

        if page_num in roman_map:
            self.setFont("Times-Roman", 10)
            self.setFillColor(CLR_TEXT_PRI)
            self.drawCentredString(PAGE_W / 2.0, 36, roman_map[page_num])
            self.restoreState()
            return

        # Chapter pages (Pages 11 onwards) -> Arabic page number starting from 1
        arabic_num = page_num - 10

        # Running Top Header
        self.setFont("Times-Bold", 10)
        self.setFillColor(CLR_TEXT_PRI)
        self.drawCentredString(PAGE_W / 2.0, PAGE_H - 32, "Cybersecurity Risk Management System")
        self.setStrokeColor(CLR_HEADER_LINE)
        self.setLineWidth(0.8)
        self.line(54, PAGE_H - 42, PAGE_W - 54, PAGE_H - 42)

        # Running Footer
        self.line(54, 52, PAGE_W - 54, 52)
        self.setFont("Times-Bold", 10)
        self.drawCentredString(PAGE_W / 2.0, 60, str(arabic_num))
        self.setFont("Times-Bold", 9.5)
        self.drawCentredString(PAGE_W / 2.0, 34, "Silver Oak College of Computer Application")

        self.restoreState()


def build_academic_pdf():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_pdf = os.path.join(root_dir, "GRC_Risk_Register_Project_Report.pdf")
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets_media")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    font_name = 'Times-Roman'
    font_bold = 'Times-Bold'
    font_italic = 'Times-Italic'

    title_crimson = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=18,
        leading=22,
        textColor=CLR_PRIMARY,
        alignment=1,
        spaceAfter=15
    )

    h1_chapter = ParagraphStyle(
        'ChapterH1',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=15,
        leading=18,
        textColor=CLR_TEXT_PRI,
        alignment=1,
        spaceBefore=8,
        spaceAfter=12,
        keepWithNext=True
    )

    ch_num_label = ParagraphStyle(
        'ChapterNum',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=13,
        leading=16,
        textColor=CLR_TEXT_PRI,
        alignment=1,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )

    h2_section = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11.5,
        leading=15,
        textColor=CLR_TEXT_PRI,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_sub = ParagraphStyle(
        'SubSectionH3',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10,
        leading=13,
        textColor=CLR_TEXT_PRI,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'AcademicBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14.5,
        textColor=CLR_TEXT_PRI,
        alignment=4,  # Justified
        spaceAfter=6
    )

    bullet = ParagraphStyle(
        'AcademicBullet',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10,
        leading=14,
        textColor=CLR_TEXT_PRI,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_header = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=9,
        leading=11.5,
        textColor=CLR_TEXT_PRI,
        alignment=0
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8.5,
        leading=11,
        textColor=CLR_TEXT_PRI
    )

    code_snippet = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=CLR_TEXT_PRI
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE PAGE (COVER)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>A PROJECT REPORT<br/>ON</b>", ParagraphStyle('ReportOn', fontName=font_bold, fontSize=13, leading=17, alignment=1)))
    story.append(Spacer(1, 24))

    story.append(Paragraph("<b>CYBERSECURITY RISK MANAGEMENT SYSTEM</b>", title_crimson))
    story.append(Spacer(1, 25))

    story.append(Paragraph("<i>Submitted to</i>", ParagraphStyle('SubTo', fontName=font_italic, fontSize=11, alignment=1)))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>The Department of Computer Application</b>", ParagraphStyle('Dept', fontName=font_bold, fontSize=13, alignment=1)))
    story.append(Spacer(1, 25))

    story.append(Paragraph("<i>In Partial fulfilment of the requirements for the<br/>3<sup>rd</sup> Semester Project of</i>", ParagraphStyle('InPartial', fontName=font_italic, fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>MASTER OF COMPUTER APPLICATION (MCA)</b>", ParagraphStyle('Degree', fontName=font_bold, fontSize=13.5, alignment=1)))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Academic Year: 2026-2027</b>", ParagraphStyle('AcadYear', fontName=font_bold, fontSize=11, alignment=1)))
    story.append(Spacer(1, 40))

    univ_block = [
        [Paragraph("<font size='15' color='#990000'><b>SILVER OAK UNIVERSITY</b></font><br/><font size='9' color='#555555'>EDUCATION TO INNOVATION</font>", ParagraphStyle('UnivB', fontName=font_bold, alignment=1))]
    ]
    univ_table = Table(univ_block, colWidths=[400])
    univ_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(univ_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Silver Oak College of Computer Application<br/>Department of Computer Application</b>", ParagraphStyle('ColDept', fontName=font_bold, fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 45))

    sub_guide = [
        [
            Paragraph("<b>Submitted By:</b>", ParagraphStyle('SB', fontName=font_bold, fontSize=10.5)),
            Paragraph("<b>Guided By:</b>", ParagraphStyle('GB', fontName=font_bold, fontSize=10.5))
        ],
        [
            Paragraph(f"{STUDENT_NAME}<br/>{ENROLLMENT_NO}", ParagraphStyle('SBN', fontName=font_name, fontSize=10, leading=14)),
            Paragraph("Mr. / Ms. Guide Name<br/>Assistant Professor, Dept. of CA", ParagraphStyle('GBN', fontName=font_name, fontSize=10, leading=14))
        ]
    ]
    t_sub_guide = Table(sub_guide, colWidths=[250, 250])
    t_sub_guide.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sub_guide)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CERTIFICATE (ii)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<font size='14' color='#990000'><b>SILVER OAK UNIVERSITY</b></font><br/><font size='8' color='#555555'>EDUCATION TO INNOVATION</font>", ParagraphStyle('CertUniv', fontName=font_bold, alignment=1)))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_BORDER, spaceBefore=0, spaceAfter=25))

    story.append(Paragraph("<b>CERTIFICATE</b>", ParagraphStyle('CertHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 25))

    story.append(Paragraph("<b>Date:</b> ______________", ParagraphStyle('CertDate', fontName=font_bold, fontSize=10.5, alignment=2)))
    story.append(Spacer(1, 30))

    cert_text = (
        f"This is to certify that the project entitled <b>“CYBERSECURITY RISK MANAGEMENT SYSTEM”</b> "
        f"has been carried out by <b>{STUDENT_NAME} ({ENROLLMENT_NO})</b> under the guidance of <b>Project Guide Name</b> in "
        f"fulfillment of the 3rd Semester Minor Project (CAM6053C) at <b>Silver Oak College of Computer Application, "
        f"Silver Oak University, Ahmedabad</b> during academic year <b>2026-2027</b>."
    )
    story.append(Paragraph(cert_text, ParagraphStyle('CertBody', parent=body, fontSize=10.5, leading=17, alignment=4)))
    story.append(Spacer(1, 160))

    cert_sig = [
        [
            Paragraph("<b>Internal Guide</b><br/>Mr./Ms. Guide Name", ParagraphStyle('IG', fontName=font_name, fontSize=10, leading=14)),
            Paragraph("<b>External Examiner</b><br/>&nbsp;", ParagraphStyle('EE', fontName=font_name, fontSize=10, leading=14, alignment=2))
        ],
        [
            Spacer(1, 55),
            Spacer(1, 55)
        ],
        [
            Paragraph("<b>Head of Department</b><br/>Department of Computer Application", ParagraphStyle('HOD', fontName=font_name, fontSize=10, leading=14, alignment=1)),
            Paragraph("", ParagraphStyle('Blank'))
        ]
    ]
    t_cert_sig = Table(cert_sig, colWidths=[250, 250])
    t_cert_sig.setStyle(TableStyle([
        ('SPAN', (0,2), (1,2)),
        ('ALIGN', (0,2), (1,2), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_cert_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: STUDENT DECLARATION (iii)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>STUDENT DECLARATION</b>", ParagraphStyle('DeclHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 35))

    decl_p1 = (
        "I hereby declare that the project entitled <b>\"CYBERSECURITY RISK MANAGEMENT SYSTEM\"</b> "
        "submitted in partial fulfilment of the requirements for the 3rd Semester of <b>Master of Computer Application (MCA)</b> "
        "is an original work carried out by me under the guidance of <b>Guide Name</b>."
    )
    decl_p2 = (
        "I further declare that this project report, or any part thereof, has not been submitted by me or any other "
        "person for the award of any other degree or diploma of this or any other university."
    )
    decl_p3 = (
        "I also declare that all the information furnished in this project report is based on my own study, analysis, "
        "and implementation, and due acknowledgement has been made wherever the work of others has been referred to."
    )
    story.append(Paragraph(decl_p1, ParagraphStyle('DP1', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(decl_p2, ParagraphStyle('DP2', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(decl_p3, ParagraphStyle('DP3', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 170))

    decl_sig = [
        [
            Paragraph("<b>Place:</b> Ahmedabad<br/><b>Date:</b> ______________", ParagraphStyle('DPlace', fontName=font_name, fontSize=10, leading=16)),
            Paragraph(f"<b>Signature of the Student</b><br/><br/>{STUDENT_NAME}<br/>Enrollment No. {ENROLLMENT_NO}", ParagraphStyle('DSig', fontName=font_name, fontSize=10, leading=15, alignment=2))
        ]
    ]
    t_decl_sig = Table(decl_sig, colWidths=[250, 250])
    t_decl_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_decl_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ACKNOWLEDGMENT (iv)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ACKNOWLEDGMENT</b>", ParagraphStyle('AckHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 30))

    ack_p1 = (
        "The development of the <b>Cybersecurity Risk Management System</b> was an engaging academic "
        "undertaking, and I am deeply grateful to all who supported its planning and completion."
    )
    ack_p2 = (
        "I extend my sincere appreciation to my project guide for providing constructive guidance and domain "
        "insights throughout the development process. Their feedback during architectural reviews and workflow "
        "evaluations helped refine the system design and implementation."
    )
    ack_p3 = (
        "I am grateful to the <b>Department of Computer Application, Silver Oak College of Computer Application</b>, "
        "for providing the lab infrastructure, development environment, and computing resources required to build "
        "and test the project."
    )
    ack_p4 = (
        "I also thank the faculty members and fellow student colleagues who participated in testing the user interface, "
        "validating risk matrix calculations, and reviewing test coverage during development reviews. Their feedback "
        "helped identify usability edge cases and improve overall reliability."
    )
    ack_p5 = (
        "This project would not have been possible without the encouragement and support of my family, teachers, and peers."
    )

    story.append(Paragraph(ack_p1, ParagraphStyle('AP1', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 12))
    story.append(Paragraph(ack_p2, ParagraphStyle('AP2', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 12))
    story.append(Paragraph(ack_p3, ParagraphStyle('AP3', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 12))
    story.append(Paragraph(ack_p4, ParagraphStyle('AP4', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 12))
    story.append(Paragraph(ack_p5, ParagraphStyle('AP5', parent=body, fontSize=10.5, leading=16)))
    story.append(Spacer(1, 75))

    story.append(Paragraph(f"{STUDENT_NAME}<br/>Enrollment No. {ENROLLMENT_NO}", ParagraphStyle('AckSig', fontName=font_name, fontSize=10, leading=14, alignment=2)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: ABSTRACT (v)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ABSTRACT</b>", ParagraphStyle('AbsHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 28))

    abs_p1 = (
        "The <b>Cybersecurity Risk Management System</b> is a lightweight, web-based application designed to streamline "
        "how small-to-midsize IT environments catalog assets, evaluate operational security risks, and track mitigations. "
        "Many organizations still track infrastructure vulnerabilities and cyber threats through ad-hoc spreadsheets. While "
        "familiar, spreadsheets offer no referential integrity between threats and assets, allow accidental formula tampering, "
        "and lack structured audit histories."
    )
    abs_p2 = (
        "To address these practical challenges, this system implements a three-tier architecture built entirely on the Python 3 "
        "Standard Library (`http.server`, `sqlite3`, `hashlib`, `secrets`) paired with a vanilla JavaScript Single Page Application. "
        "The system enforces role-based access control (Admin and Analyst roles), maintains relational asset inventories, evaluates "
        "threat scenarios on a deterministic 3x3 qualitative matrix (Likelihood x Impact), tracks lifecycle remediation statuses "
        "(Open, In Progress, Treated, Closed), and logs every modification to an immutable audit ledger."
    )
    abs_p3 = (
        "The primary design goal was zero-configuration portability: the application runs locally with zero external package "
        "dependencies (`pip install` free) while maintaining complete ACID compliance through SQLite. A comprehensive automated "
        "test suite of 33 test cases verified API routes, session token generation, mathematical scoring boundaries, and data integrity."
    )
    abs_p4 = (
        "The resulting system provides a secure, consistent, and easily deployable tool for institutional cybersecurity governance "
        "and forms a practical foundation for future risk management extensions."
    )

    story.append(Paragraph(abs_p1, ParagraphStyle('AbP1', parent=body, fontSize=10, leading=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(abs_p2, ParagraphStyle('AbP2', parent=body, fontSize=10, leading=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(abs_p3, ParagraphStyle('AbP3', parent=body, fontSize=10, leading=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(abs_p4, ParagraphStyle('AbP4', parent=body, fontSize=10, leading=15)))
    story.append(Spacer(1, 20))

    story.append(Paragraph("<b>Keywords:</b> Cybersecurity Risk Management System, Automation, Database Management System (DBMS), SDLC, Web Application, Risk Assessment, GRC.", ParagraphStyle('KW', fontName=font_bold, fontSize=9.5, leading=14)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: TABLE OF CONTENTS (Part 1 - vi)
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>TABLE OF CONTENTS</b>", ParagraphStyle('TOCHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 20))

    toc_page1 = [
        ("Title Page", "i"),
        ("Certificate", "ii"),
        ("Student Declaration", "iii"),
        ("Acknowledgement", "iv"),
        ("Abstract", "v"),
        ("Table of Contents", "vi"),
        ("List of Figures", "viii"),
        ("List of Tables", "ix"),
        ("List of Abbreviations", "x"),
        ("<b>Chapter 1: Introduction</b>", "<b>1</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.1 Background", "1"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.2 Problem Statement", "2"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.3 Objectives of the Project", "2"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.4 Scope of the Project", "2"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;1.5 Organization of the Report", "2"),
        ("<b>Chapter 2: Literature Review</b>", "<b>3</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.1 Existing Systems", "3"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.2 Comparative Analysis", "3"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;2.3 Summary", "3"),
        ("<b>Chapter 3: System Requirement Analysis</b>", "<b>4</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.1 Functional Requirements", "4"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.2 Non-Functional Requirements", "4"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.3 Hardware Requirements", "4"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.4 Software Requirements", "5"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;3.5 Feasibility Study", "5"),
        ("<b>Chapter 4: System Design and Methodology</b>", "<b>6</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.1 System Architecture", "6"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.2 Data Flow Diagrams", "6"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.3 Entity-Relationship Diagram", "6"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.4 Database Design", "6"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;4.5 UML Diagrams", "7"),
        ("<b>Chapter 5: Implementation and Coding</b>", "<b>8</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;5.1 Development Environment", "8"),
    ]

    t_data_p1 = []
    for title_txt, pg in toc_page1:
        p_title = Paragraph(title_txt, ParagraphStyle('TOCItem', fontName=font_name, fontSize=9.5, leading=13))
        p_page = Paragraph(pg, ParagraphStyle('TOCPg', fontName=font_name, fontSize=9.5, leading=13, alignment=2))
        t_data_p1.append([p_title, p_page])

    t_toc1 = Table(t_data_p1, colWidths=[430, 70])
    t_toc1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 1.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
    ]))
    story.append(t_toc1)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: TABLE OF CONTENTS (Part 2 - vii)
    # =========================================================================
    story.append(Spacer(1, 15))
    toc_page2 = [
        ("&nbsp;&nbsp;&nbsp;&nbsp;5.2 Module Description", "8"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;5.3 Coding Standards", "8"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;5.4 Sample Code Snippets", "9"),
        ("<b>Chapter 6: Testing and Results Analysis</b>", "<b>10</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.1 Testing Objectives", "10"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.2 Testing Methods", "10"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.3 Test Cases", "10"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;6.4 Results Analysis", "11"),
        ("<b>Chapter 7: Conclusion and Future Scope</b>", "<b>12</b>"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;7.1 Conclusion", "12"),
        ("&nbsp;&nbsp;&nbsp;&nbsp;7.2 Future Scope", "12"),
        ("<b>Bibliography & References</b>", "<b>13</b>"),
        ("<b>Appendices</b>", "<b>14</b>"),
        ("<b>Publication / Patent / Research Output</b>", "<b>18</b>"),
    ]

    t_data_p2 = []
    for title_txt, pg in toc_page2:
        p_title = Paragraph(title_txt, ParagraphStyle('TOCItem2', fontName=font_name, fontSize=9.5, leading=14))
        p_page = Paragraph(pg, ParagraphStyle('TOCPg2', fontName=font_name, fontSize=9.5, leading=14, alignment=2))
        t_data_p2.append([p_title, p_page])

    t_toc2 = Table(t_data_p2, colWidths=[430, 70])
    t_toc2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_toc2)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: LIST OF FIGURES (viii)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF FIGURES</b>", ParagraphStyle('LOFHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 25))

    lof_data = [
        [Paragraph("<b>Figure No.</b>", table_header), Paragraph("<b>Title</b>", table_header), Paragraph("<b>Page No.</b>", table_header)],
        [Paragraph("Figure 3.1", table_cell), Paragraph("Use Case Diagram of Cybersecurity Risk Management System", table_cell), Paragraph("5", table_cell)],
        [Paragraph("Figure 4.1", table_cell), Paragraph("System Architecture Diagram", table_cell), Paragraph("6", table_cell)],
        [Paragraph("Figure 4.2", table_cell), Paragraph("Data Flow Diagram (Level 0)", table_cell), Paragraph("6", table_cell)],
        [Paragraph("Figure 4.3", table_cell), Paragraph("Data Flow Diagram (Level 1)", table_cell), Paragraph("6", table_cell)],
        [Paragraph("Figure 4.4", table_cell), Paragraph("Entity-Relationship Diagram", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Figure 4.5", table_cell), Paragraph("Class Diagram", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Figure 4.6", table_cell), Paragraph("Sequence Diagram — Risk Assessment & Evaluation Process", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Figure 5.1", table_cell), Paragraph("Login Module Screenshot", table_cell), Paragraph("9", table_cell)],
        [Paragraph("Figure 5.2", table_cell), Paragraph("Executive Dashboard & Risk Heatmap Screenshot", table_cell), Paragraph("9", table_cell)],
        [Paragraph("Figure 6.1", table_cell), Paragraph("Graph Showing Test Case Pass/Fail Ratio", table_cell), Paragraph("11", table_cell)],
    ]
    t_lof = Table(lof_data, colWidths=[80, 340, 80])
    t_lof.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_lof)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: LIST OF TABLES (ix)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF TABLES</b>", ParagraphStyle('LOTHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 25))

    lot_data = [
        [Paragraph("<b>Table No.</b>", table_header), Paragraph("<b>Title</b>", table_header), Paragraph("<b>Page No.</b>", table_header)],
        [Paragraph("Table 3.1", table_cell), Paragraph("Functional Requirements", table_cell), Paragraph("4", table_cell)],
        [Paragraph("Table 3.2", table_cell), Paragraph("Hardware Requirements", table_cell), Paragraph("4", table_cell)],
        [Paragraph("Table 3.3", table_cell), Paragraph("Software Requirements", table_cell), Paragraph("5", table_cell)],
        [Paragraph("Table 4.1", table_cell), Paragraph("Database Table — tbl_Asset", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Table 4.2", table_cell), Paragraph("Database Table — tbl_Risk", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Table 4.3", table_cell), Paragraph("Database Table — tbl_AuditLog", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Table 6.1", table_cell), Paragraph("Test Cases for Login Module", table_cell), Paragraph("10", table_cell)],
        [Paragraph("Table 6.2", table_cell), Paragraph("Test Cases for Asset Inventory Module", table_cell), Paragraph("10", table_cell)],
        [Paragraph("Table 6.3", table_cell), Paragraph("Test Cases for Risk Calculation Module", table_cell), Paragraph("11", table_cell)],
    ]
    t_lot = Table(lot_data, colWidths=[80, 340, 80])
    t_lot.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_lot)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: LIST OF ABBREVIATIONS (x)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF ABBREVIATIONS</b>", ParagraphStyle('LOAHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 25))

    loa_data = [
        [Paragraph("<b>Abbreviation</b>", table_header), Paragraph("<b>Full Form & Technical Meaning</b>", table_header)],
        [Paragraph("ACID", table_cell), Paragraph("<b>Atomicity, Consistency, Isolation, Durability:</b> Database transaction guarantees that ensure records are never half-written or corrupted during failures.", table_cell)],
        [Paragraph("PBKDF2", table_cell), Paragraph("<b>Password-Based Key Derivation Function 2:</b> Key stretching algorithm applying repeated pseudorandom hashing rounds to defeat brute-force password cracking.", table_cell)],
        [Paragraph("HMAC", table_cell), Paragraph("<b>Hash-based Message Authentication Code:</b> Cryptographic construction combining a secret key with a hash function for message authenticity and data integrity.", table_cell)],
        [Paragraph("SHA-256", table_cell), Paragraph("<b>Secure Hash Algorithm (256-bit):</b> Cryptographic one-way hash function producing a 32-byte deterministic fingerprint.", table_cell)],
        [Paragraph("GRC", table_cell), Paragraph("<b>Governance, Risk, and Compliance:</b> Strategy for managing IT risk and aligning technology with regulatory compliance standards.", table_cell)],
        [Paragraph("RBAC", table_cell), Paragraph("<b>Role-Based Access Control:</b> Security mechanism restricting system access permissions based on authorized user roles (Admin vs. Analyst).", table_cell)],
        [Paragraph("NIST", table_cell), Paragraph("<b>National Institute of Standards and Technology:</b> U.S. federal agency establishing cybersecurity standards (e.g., NIST SP 800-30 for risk assessment).", table_cell)],
        [Paragraph("SDLC", table_cell), Paragraph("<b>Software Development Life Cycle:</b> Structured framework for designing, implementing, testing, and deploying reliable software.", table_cell)],
        [Paragraph("DFD", table_cell), Paragraph("<b>Data Flow Diagram:</b> Graphical representation tracing the flow and transformation of data through system processes.", table_cell)],
        [Paragraph("ER Diagram", table_cell), Paragraph("<b>Entity-Relationship Diagram:</b> Database schema model illustrating tables, primary/foreign keys, and relational cardinality.", table_cell)],
        [Paragraph("UML", table_cell), Paragraph("<b>Unified Modeling Language:</b> Standard software engineering modeling language for visualizing architecture, classes, and sequences.", table_cell)],
        [Paragraph("CRUD", table_cell), Paragraph("<b>Create, Read, Update, Delete:</b> The four fundamental persistent operations of storage applications.", table_cell)],
        [Paragraph("GUI", table_cell), Paragraph("<b>Graphical User Interface:</b> Visual display elements (buttons, inputs, tables) allowing intuitive interaction without command lines.", table_cell)],
        [Paragraph("SQL", table_cell), Paragraph("<b>Structured Query Language:</b> Declarative domain-specific language for managing structured relational database records.", table_cell)],
        [Paragraph("IDE", table_cell), Paragraph("<b>Integrated Development Environment:</b> Software application providing comprehensive tools (editor, debugger) for software engineering.", table_cell)],
    ]
    t_loa = Table(loa_data, colWidths=[90, 410])
    t_loa.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_loa)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11 (Body Page 1): CHAPTER 1 — Introduction (1.1, 1.2, 1.3)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 1</b>", ch_num_label))
    story.append(Paragraph("<b>Introduction</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>1.1 Background</b>", h2_section))
    intro_bg = (
        "Organizations manage a diverse mix of IT assets, including customer data repositories, server operating systems, "
        "network gateways, and internal web services. Each asset presents specific exposure points to operational disruption, "
        "data loss, or configuration drift. Historically, institutional departments have tracked these risks using manual paperwork, "
        "shared spreadsheets, and email chains. However, as the number of assets and compliance requirements increases, spreadsheet-based "
        "methods struggle to maintain data consistency.<br/><br/>"
        "Without strict relational controls, formulas for severity ratings are easily corrupted, asset classifications vary across teams, "
        "and tracking who modified a risk status becomes difficult. Computerizing this workflow into a dedicated risk management system "
        "replaces informal record-keeping with structured validation, automated calculations, and a dependable audit record."
    )
    story.append(Paragraph(intro_bg, body))

    story.append(Paragraph("<b>1.2 Problem Statement</b>", h2_section))
    intro_ps = (
        "Manual risk registers suffer from three consistent bottlenecks: first, lack of relational validation allows risks to reference "
        "non-existent or deleted assets; second, qualitative scoring is often subjective and inconsistent when calculated manually by "
        "different evaluators; third, shared files lack change accountability and user access boundaries. The objective of this project "
        "is to provide a centralized, computerized platform that enforces relational integrity between assets and threats, calculates "
        "risk levels objectively, and preserves an immutable audit log."
    )
    story.append(Paragraph(intro_ps, body))

    story.append(Paragraph("<b>1.3 Objectives of the Project</b>", h2_section))
    story.append(Paragraph("• To design and build a relational database storing organizational assets, threat scenarios, and audit logs.", bullet))
    story.append(Paragraph("• To automate qualitative risk evaluation using a standardized 3x3 matrix based on Likelihood and Impact.", bullet))
    story.append(Paragraph("• To provide an intuitive search and filtering mechanism to locate records by severity, category, or status.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12 (Body Page 2): CHAPTER 1 — Introduction (1.3 cont., 1.4, 1.5)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("• To generate executive reporting summaries, including distribution heatmaps and treatment progress.", bullet))
    story.append(Paragraph("• To enforce role-based access control distinguishing administrative permissions from analyst reviews.", bullet))
    story.append(Paragraph("• To eliminate external library dependencies by running entirely on standard runtime libraries.", bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.4 Scope of the Project</b>", h2_section))
    intro_scope = (
        "The project encompasses core functional areas of institutional cybersecurity risk governance: asset registration (Data, System, "
        "Device, Service), threat scenario cataloguing, qualitative risk matrix computation (Low, Medium, High), lifecycle treatment tracking "
        "(Open, In Progress, Treated, Closed), and automated immutable audit logging. The system is engineered as an on-premise, privacy-first "
        "solution operating over local HTTP/JSON protocols. External vulnerability scanner feeds and cloud synchronizations are outside "
        "the current scope and are planned for future versions."
    )
    story.append(Paragraph(intro_scope, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.5 Organization of the Report</b>", h2_section))
    intro_org = (
        "This report is organized into seven structured chapters: Chapter 1 introduces the project background, problem statement, "
        "objectives, and scope. Chapter 2 reviews literature and comparative systems. Chapter 3 details system requirements and feasibility. "
        "Chapter 4 presents system architecture, DFDs, ER diagrams, and database schemas. Chapter 5 covers implementation, modules, and coding "
        "standards. Chapter 6 analyzes testing strategies and test cases. Finally, Chapter 7 concludes with key findings and future scope."
    )
    story.append(Paragraph(intro_org, body))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13 (Body Page 3): CHAPTER 2 — Literature Review (2.1, 2.2, 2.3)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 2</b>", ch_num_label))
    story.append(Paragraph("<b>Literature Review</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2.1 Existing Systems</b>", h2_section))
    lit_ex = (
        "Organizations typically choose between two extremes for managing cybersecurity risks. On one end, enterprise governance suites "
        "such as ServiceNow GRC and RSA Archer offer deep workflow automation but demand substantial infrastructure, complex database setups, "
        "and costly licensing that is impractical for academic departments or smaller IT teams.<br/><br/>"
        "On the other end, spreadsheets remain common due to their familiarity and zero acquisition cost. However, academic studies in software "
        "quality highlight that spreadsheets lack atomic transaction guarantees, provide no granular access control, and are vulnerable to "
        "silent formula corruption during routine data entry."
    )
    story.append(Paragraph(lit_ex, body))

    story.append(Paragraph("<b>2.2 Comparative Analysis</b>", h2_section))
    lit_comp = (
        "A comparative review demonstrates that while commercial platforms provide extensive capabilities, their operational overhead "
        "is excessive for focused departmental use. Conversely, spreadsheets lack relational rigor. The proposed Cybersecurity Risk Management "
        "System addresses this gap by combining the lightweight portability of a single-file server with the ACID guarantees, schema validation, "
        "and audit trails of a relational database."
    )
    story.append(Paragraph(lit_comp, body))

    story.append(Paragraph("<b>2.3 Summary</b>", h2_section))
    lit_sum = (
        "The literature underscores the need for accessible, structured tools that automate risk assessment without requiring heavy "
        "third-party infrastructure. By grounding calculations in recognized NIST SP 800-30 qualitative principles, the system delivers "
        "consistent risk governance in an efficient, self-contained architecture."
    )
    story.append(Paragraph(lit_sum, body))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 14 (Body Page 4): CHAPTER 3 — System Requirement Analysis (3.1, 3.2, 3.3)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 3</b>", ch_num_label))
    story.append(Paragraph("<b>System Requirement Analysis</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>3.1 Functional Requirements</b>", h2_section))
    story.append(Paragraph("Functional requirements define the core capabilities and operational behaviors supported by the system. Table 3.1 details the verified functional requirements.", body))

    fr_data = [
        [Paragraph("<b>Req. ID</b>", table_header), Paragraph("<b>Requirement Description</b>", table_header)],
        [Paragraph("FR-1", table_cell), Paragraph("The system shall allow administrators to add, update, and archive asset records.", table_cell)],
        [Paragraph("FR-2", table_cell), Paragraph("The system shall allow registration and management of cybersecurity risk scenarios.", table_cell)],
        [Paragraph("FR-3", table_cell), Paragraph("The system shall link risk scenarios to specific assets using relational foreign keys.", table_cell)],
        [Paragraph("FR-4", table_cell), Paragraph("The system shall automatically compute risk scores from Likelihood and Impact ratings.", table_cell)],
        [Paragraph("FR-5", table_cell), Paragraph("The system shall allow searching and filtering of risks by title, asset, category, or status.", table_cell)],
        [Paragraph("FR-6", table_cell), Paragraph("The system shall generate executive summaries, heatmaps, and audit trail logs.", table_cell)],
        [Paragraph("FR-7", table_cell), Paragraph("The system shall provide role-based login distinguishing Admin and Analyst permissions.", table_cell)],
    ]
    t_fr = Table(fr_data, colWidths=[70, 430])
    t_fr.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_fr)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>3.2 Non-Functional Requirements</b>", h2_section))
    story.append(Paragraph("• <b>Usability:</b> Clean single-page browser interface with interactive modal forms and real-time calculation previews.", bullet))
    story.append(Paragraph("• <b>Reliability (ACID Guarantees):</b> Complete ACID transactional safety (<i>Atomicity</i>: all-or-nothing commits; <i>Consistency</i>: foreign-key validation; <i>Isolation</i>: serial database operations; <i>Durability</i>: write-ahead logging to disk) via SQLite.", bullet))
    story.append(Paragraph("• <b>Performance:</b> API query and calculation response times under 50 milliseconds on standard hardware.", bullet))
    story.append(Paragraph("• <b>Security (Cryptographic Hashing):</b> Passwords protected via <b>PBKDF2-HMAC-SHA256</b> (Password-Based Key Derivation Function 2 using Hash-based Message Authentication with SHA-256) running 100,000 iterative hashing rounds with 16-byte random salts to defeat brute-force and rainbow table attacks.", bullet))
    story.append(Paragraph("• <b>Portability:</b> Native execution on Python 3 with zero external pip package dependencies.", bullet))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>3.3 Hardware Requirements</b>", h2_section))
    hw_data = [
        [Paragraph("<b>Component</b>", table_header), Paragraph("<b>Specification</b>", table_header)],
        [Paragraph("Processor", table_cell), Paragraph("Intel Core i3 / AMD Ryzen 3 or equivalent x86-64 / ARM64", table_cell)],
        [Paragraph("RAM", table_cell), Paragraph("2 GB RAM minimum (4 GB recommended)", table_cell)],
        [Paragraph("Hard Disk", table_cell), Paragraph("50 MB free disk storage", table_cell)],
        [Paragraph("Monitor", table_cell), Paragraph("Standard colour display (1024 x 768 or higher)", table_cell)],
    ]
    t_hw = Table(hw_data, colWidths=[150, 350])
    t_hw.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_hw)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 15 (Body Page 5): CHAPTER 3 — Requirements (3.4 Software, 3.5 Feasibility, Use Case)
    # =========================================================================
    story.append(Paragraph("<b>3.4 Software Requirements</b>", h2_section))
    sw_data = [
        [Paragraph("<b>Component</b>", table_header), Paragraph("<b>Specification</b>", table_header)],
        [Paragraph("Operating System", table_cell), Paragraph("Windows 10 / 11, Linux (Ubuntu/Debian), macOS 11+", table_cell)],
        [Paragraph("Front-End", table_cell), Paragraph("HTML5, CSS3, Vanilla JavaScript (ES6+)", table_cell)],
        [Paragraph("Back-End", table_cell), Paragraph("Python 3.8+ (Standard Library: http.server, sqlite3, hashlib, secrets)", table_cell)],
        [Paragraph("Database", table_cell), Paragraph("SQLite 3 (Embedded relational database)", table_cell)],
        [Paragraph("IDE", table_cell), Paragraph("Visual Studio Code", table_cell)],
    ]
    t_sw = Table(sw_data, colWidths=[150, 350])
    t_sw.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_sw)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>3.5 Feasibility Study</b>", h2_section))
    story.append(Paragraph("<b>3.5.1 Technical Feasibility</b>", h3_sub))
    story.append(Paragraph(
        "The project uses Python's built-in HTTP server and embedded SQLite database. Because these tools are part of the core "
        "Python installation, deployment requires no complex environment configuration or external package managers.", body
    ))

    story.append(Paragraph("<b>3.5.2 Economic Feasibility</b>", h3_sub))
    story.append(Paragraph(
        "All development tools, runtimes, and libraries used are open-source and freely available. The software requires no recurring "
        "license fees or specialized server hardware, making it economically practical for educational and departmental settings.", body
    ))

    story.append(Paragraph("<b>3.5.3 Operational Feasibility</b>", h3_sub))
    story.append(Paragraph(
        "The browser-based interface follows standard design conventions with intuitive navigation tabs, immediate validation feedback, "
        "and clear risk categorization, minimizing training requirements for operational staff.", body
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<i>[Figure 3.1: Use Case Diagram of Cybersecurity Risk Management System — to be inserted here]</i>", ParagraphStyle('FigNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 16 (Body Page 6): CHAPTER 4 — System Design and Methodology (4.1, 4.2, 4.3, 4.4)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 4</b>", ch_num_label))
    story.append(Paragraph("<b>System Design and Methodology</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>4.1 System Architecture</b>", h2_section))
    story.append(Paragraph(
        "The application follows a clean Three-Tier Architecture. The <b>Presentation Layer</b> is a responsive client application "
        "rendering dynamic tables, modal dialogues, and heatmaps without bulky JavaScript frameworks. The <b>Application Layer</b> "
        "is a Python HTTP server handling REST endpoints, input sanitization, PBKDF2 authentication, and matrix calculations. The "
        "<b>Data Layer</b> is an embedded SQLite database enforcing ACID consistency and foreign-key referential integrity.", body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>[Figure 4.1: System Architecture Diagram — to be inserted here]</i>", ParagraphStyle('F41', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.2 Data Flow Diagrams</b>", h2_section))
    story.append(Paragraph(
        "The Data Flow Diagram illustrates how information moves across system boundaries. The Level 0 DFD represents user interactions "
        "with the central risk register boundary. The Level 1 DFD decomposes this interaction into four distinct internal processes: "
        "Session Authentication, Asset Cataloguing, Risk Calculation Engine, and Audit Ledger Recording.", body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>[Figure 4.2: Data Flow Diagram (Level 0) — to be inserted here]</i>", ParagraphStyle('F42', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Paragraph("<i>[Figure 4.3: Data Flow Diagram (Level 1) — to be inserted here]</i>", ParagraphStyle('F43', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.3 Entity-Relationship Diagram</b>", h2_section))
    story.append(Paragraph(
        "The data model is structured around a one-to-many relationship between Assets and Risks. Each asset can link to multiple "
        "identified threat scenarios, while each risk references exactly one parent asset. A separate AuditLog entity records every "
        "insert, update, and archive operation with user attribution.", body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>[Figure 4.4: Entity-Relationship Diagram — to be inserted here]</i>", ParagraphStyle('F44', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.4 Database Design</b>", h2_section))
    story.append(Paragraph("The database consists of three primary tables designed with explicit types and constraints, detailed on the following page.", body))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 17 (Body Page 7): CHAPTER 4 — Database Design Tables & 4.5 UML Diagrams
    # =========================================================================
    story.append(Paragraph("<b>4.4.1 tbl_Asset</b>", h3_sub))
    ast_cols = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>Data Type</b>", table_header), Paragraph("<b>Description</b>", table_header)],
        [Paragraph("AssetID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique internal identifier (Auto-increment)", table_cell)],
        [Paragraph("Name", table_cell), Paragraph("Varchar(150)", table_cell), Paragraph("Asset title or hardware designation", table_cell)],
        [Paragraph("Type", table_cell), Paragraph("Varchar(50)", table_cell), Paragraph("Classification (Data, System, Device, Service)", table_cell)],
        [Paragraph("Owner", table_cell), Paragraph("Varchar(100)", table_cell), Paragraph("Designated custodian or department", table_cell)],
    ]
    t_ast = Table(ast_cols, colWidths=[120, 100, 280])
    t_ast.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_ast)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.4.2 tbl_Risk</b>", h3_sub))
    rsk_cols = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>Data Type</b>", table_header), Paragraph("<b>Description</b>", table_header)],
        [Paragraph("RiskID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique internal identifier (Auto-increment)", table_cell)],
        [Paragraph("Title", table_cell), Paragraph("Varchar(200)", table_cell), Paragraph("Threat scenario description", table_cell)],
        [Paragraph("AssetID", table_cell), Paragraph("Int (FK)", table_cell), Paragraph("Foreign key referencing tbl_Asset(AssetID)", table_cell)],
        [Paragraph("Likelihood", table_cell), Paragraph("Int", table_cell), Paragraph("Rating scale: 1 (Low), 2 (Medium), 3 (High)", table_cell)],
        [Paragraph("Impact", table_cell), Paragraph("Int", table_cell), Paragraph("Rating scale: 1 (Low), 2 (Medium), 3 (High)", table_cell)],
        [Paragraph("Score", table_cell), Paragraph("Int", table_cell), Paragraph("Computed product: Likelihood x Impact (1-9)", table_cell)],
        [Paragraph("Status", table_cell), Paragraph("Varchar(30)", table_cell), Paragraph("Stage: Open, In Progress, Treated, Closed", table_cell)],
    ]
    t_rsk = Table(rsk_cols, colWidths=[120, 100, 280])
    t_rsk.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rsk)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.4.3 tbl_AuditLog</b>", h3_sub))
    aud_cols = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>Data Type</b>", table_header), Paragraph("<b>Description</b>", table_header)],
        [Paragraph("LogID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Sequential event record identifier", table_cell)],
        [Paragraph("Action", table_cell), Paragraph("Varchar(50)", table_cell), Paragraph("Mutation type (CREATE, UPDATE, ARCHIVE)", table_cell)],
        [Paragraph("UserID", table_cell), Paragraph("Int", table_cell), Paragraph("User who initiated the transaction", table_cell)],
        [Paragraph("Timestamp", table_cell), Paragraph("Datetime", table_cell), Paragraph("UTC recorded time of database commit", table_cell)],
    ]
    t_aud = Table(aud_cols, colWidths=[120, 100, 280])
    t_aud.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_aud)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>4.5 UML Diagrams</b>", h2_section))
    story.append(Paragraph(
        "System modeling used standard UML diagrams: the Use Case Diagram defines actor interactions, the Class Diagram represents "
        "service handlers and data access objects, and the Sequence Diagram documents the step-by-step risk calculation and validation flow.", body
    ))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<i>[Figure 4.5: Class Diagram — to be inserted here]</i>", ParagraphStyle('F45', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Paragraph("<i>[Figure 4.6: Sequence Diagram — Risk Assessment Process — to be inserted here]</i>", ParagraphStyle('F46', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 18 (Body Page 8): CHAPTER 5 — Implementation and Coding (5.1, 5.2, 5.3)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 5</b>", ch_num_label))
    story.append(Paragraph("<b>Implementation and Coding</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>5.1 Development Environment</b>", h2_section))
    story.append(Paragraph(
        "Development was carried out in Visual Studio Code on Windows 11 with Python 3.11. The implementation relies on standard "
        "library packages: `http.server` for HTTP routing, `sqlite3` for persistence, `hashlib` for cryptographic hashing, and `secrets` "
        "for secure session token generation. Git was used for source revision control.", body
    ))

    story.append(Paragraph("<b>5.2 Module Description</b>", h2_section))
    story.append(Paragraph("<b>5.2.1 Login Module:</b> Manages user authentication using salted <b>PBKDF2-HMAC-SHA256</b> (Password-Based Key Derivation Function 2 with Hash-based Message Authentication Code using SHA-256). For each credential verification, the system combines the plaintext password with a unique 16-byte random salt and executes 100,000 recursive hashing rounds. This deliberate computational cost makes offline dictionary and rainbow-table attacks unfeasible. Validates active cryptographically secure session tokens and enforces Role-Based Access Control (Admin vs. Analyst).", body))
    story.append(Paragraph("<b>5.2.2 Asset Management Module:</b> Provides endpoints for registering, editing, and soft-archiving organizational assets. Validates required names, classifies types, and ensures asset records cannot be hard-deleted if referenced by risks.", body))
    story.append(Paragraph("<b>5.2.3 Risk Assessment Module:</b> Manages the creation and tracking of threat scenarios linked to specific assets. Enforces allowed status transitions across Open, In Progress, Treated, and Closed.", body))
    story.append(Paragraph("<b>5.2.4 Calculation Module:</b> Implements the qualitative 3x3 evaluation engine. Computes the product of Likelihood and Impact ratings and maps scores to discrete severity categories (Low: 1-2, Medium: 3-4, High: 6-9).", body))
    story.append(Paragraph("<b>5.2.5 Report Module:</b> Generates executive summary metrics, including risk level counts, treatment distribution, interactive matrix coordinates, and exportable data tables.", body))

    story.append(Paragraph("<b>5.3 Coding Standards</b>", h2_section))
    story.append(Paragraph(
        "The codebase follows PEP 8 standards with descriptive naming and modular helper functions. All SQL queries use parameterized "
        "prepared statements to prevent SQL injection vulnerabilities. Client-side JavaScript is written in modern ES6+ with dedicated "
        "handlers for API communication.", body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 19 (Body Page 9): CHAPTER 5 — Snippets & Screenshots
    # =========================================================================
    story.append(Paragraph("<b>5.4 Sample Code Snippets</b>", h2_section))
    story.append(Paragraph(
        "The following code snippet demonstrates the deterministic risk calculation logic implemented in the backend application:", body
    ))
    story.append(Spacer(1, 4))

    calc_python = (
        "def calculate_risk_score(likelihood: int, impact: int) -&gt; dict:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;if not (1 &lt;= likelihood &lt;= 3 and 1 &lt;= impact &lt;= 3):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;raise ValueError('Ratings must be between 1 and 3')<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;score = likelihood * impact<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;if score &lt;= 2: level = 'Low'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;elif score &lt;= 4: level = 'Medium'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;else: level = 'High'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return {'score': score, 'level': level}"
    )
    t_snip = Table([[Paragraph(calc_python, code_snippet)]], colWidths=[500])
    t_snip.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CLR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_snip)
    story.append(Spacer(1, 10))

    img_login = os.path.join(media_dir, "screen_login.png")
    if os.path.exists(img_login):
        story.append(Paragraph("<b>Figure 5.1: Login Module Screenshot</b>", h3_sub))
        story.append(Spacer(1, 2))
        story.append(Image(img_login, width=320, height=130))
        story.append(Spacer(1, 8))

    img_dash = os.path.join(media_dir, "screen_dashboard.png")
    if os.path.exists(img_dash):
        story.append(Paragraph("<b>Figure 5.2: Executive Dashboard & Risk Heatmap Screenshot</b>", h3_sub))
        story.append(Spacer(1, 2))
        story.append(Image(img_dash, width=440, height=160))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 20 (Body Page 10): CHAPTER 6 — Testing and Results Analysis (6.1, 6.2, 6.3)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 6</b>", ch_num_label))
    story.append(Paragraph("<b>Testing and Results Analysis</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>6.1 Testing Objectives</b>", h2_section))
    story.append(Paragraph(
        "Testing was conducted to verify that all functional requirements, mathematical boundary constraints, session security mechanisms, "
        "and database transactions operate correctly without data leakage or unexpected runtime errors.", body
    ))

    story.append(Paragraph("<b>6.2 Testing Methods</b>", h2_section))
    story.append(Paragraph(
        "A multi-stage testing approach was implemented using Python's native `unittest` framework. Unit testing verified individual "
        "calculation routines and password hashing algorithms. Integration testing verified complete HTTP request/response cycles and "
        "database foreign key constraints. User acceptance testing was conducted using realistic test scenarios.", body
    ))

    story.append(Paragraph("<b>6.3 Test Cases</b>", h2_section))
    story.append(Paragraph("<b>6.3.1 Login Module</b>", h3_sub))

    tc_login = [
        [Paragraph("<b>Test Case ID</b>", table_header), Paragraph("<b>Description</b>", table_header), Paragraph("<b>Expected Result</b>", table_header), Paragraph("<b>Status</b>", table_header)],
        [Paragraph("TC-01", table_cell), Paragraph("Login with valid credentials", table_cell), Paragraph("Session created; user redirected to dashboard", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-02", table_cell), Paragraph("Login with invalid password", table_cell), Paragraph("HTTP 401 returned; error message displayed", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc1 = Table(tc_login, colWidths=[70, 150, 220, 60])
    t_tc1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>6.3.2 Asset Inventory Module</b>", h3_sub))
    tc_asset = [
        [Paragraph("<b>Test Case ID</b>", table_header), Paragraph("<b>Description</b>", table_header), Paragraph("<b>Expected Result</b>", table_header), Paragraph("<b>Status</b>", table_header)],
        [Paragraph("TC-04", table_cell), Paragraph("Add new valid IT asset", table_cell), Paragraph("Asset created; formatted ID assigned", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-05", table_cell), Paragraph("Add asset with missing name", table_cell), Paragraph("HTTP 400 returned: name required", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc2 = Table(tc_asset, colWidths=[70, 150, 220, 60])
    t_tc2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc2)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>6.3.3 Risk Calculation Module</b>", h3_sub))
    tc_calc = [
        [Paragraph("<b>Test Case ID</b>", table_header), Paragraph("<b>Description</b>", table_header), Paragraph("<b>Expected Result</b>", table_header), Paragraph("<b>Status</b>", table_header)],
        [Paragraph("TC-07", table_cell), Paragraph("Calculate Low Risk (1 x 2)", table_cell), Paragraph("Score 2; qualitative level 'Low' assigned", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc3 = Table(tc_calc, colWidths=[70, 150, 220, 60])
    t_tc3.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc3)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 21 (Body Page 11): CHAPTER 6 — Test Cases cont. & 6.4 Results Analysis
    # =========================================================================
    story.append(Spacer(1, 10))
    tc_calc_cont = [
        [Paragraph("<b>Test Case ID</b>", table_header), Paragraph("<b>Description</b>", table_header), Paragraph("<b>Expected Result</b>", table_header), Paragraph("<b>Status</b>", table_header)],
        [Paragraph("TC-08", table_cell), Paragraph("Calculate High Risk (3 x 3)", table_cell), Paragraph("Score 9; qualitative level 'High' assigned", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-09", table_cell), Paragraph("Link risk to non-existent asset", table_cell), Paragraph("Foreign key violation raised and rejected", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-10", table_cell), Paragraph("Audit log recording on risk edit", table_cell), Paragraph("Audit record inserted with timestamp and user ID", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc_cont = Table(tc_calc_cont, colWidths=[70, 150, 220, 60])
    t_tc_cont.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc_cont)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>6.4 Results Analysis</b>", h2_section))
    results_text = (
        "The automated test suite executed all <b>33 test cases</b> across 7 test modules in <b>4.43 seconds</b> with a <b>100% pass "
        "rate (0 failures, 0 errors)</b>. The test results confirm that all REST endpoints, password encryption routines, scoring boundary "
        "validations, and database relational constraints behave as expected. Initial issues identified during testing, such as edge-case "
        "string sanitization in search queries, were corrected before final packaging."
    )
    story.append(Paragraph(results_text, body))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<i>[Figure 6.1: Graph Showing Test Case Pass/Fail Ratio — to be inserted here]</i>", ParagraphStyle('F61', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 22 (Body Page 12): CHAPTER 7 — Conclusion and Future Scope
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 7</b>", ch_num_label))
    story.append(Paragraph("<b>Conclusion and Future Scope</b>", h1_chapter))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>7.1 Conclusion</b>", h2_section))
    conc_text = (
        "The Cybersecurity Risk Management System provides a reliable, self-contained solution for institutional risk tracking. "
        "By replacing error-prone spreadsheets with an ACID-compliant SQLite backend and deterministic qualitative matrix evaluation, "
        "the application eliminates scoring ambiguity, ensures referential integrity between threats and assets, and provides a clear "
        "historical audit trail. Running entirely on the Python Standard Library without external packages makes the system easy to deploy "
        "and maintain in any computing environment."
    )
    story.append(Paragraph(conc_text, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>7.2 Future Scope</b>", h2_section))
    story.append(Paragraph("• Integration with standardized vulnerability data feeds (such as CVE/NVD) for automated risk scenario drafting.", bullet))
    story.append(Paragraph("• Quantitative risk analysis extensions implementing Monte Carlo simulations for financial loss expectancy.", bullet))
    story.append(Paragraph("• Multi-Factor Authentication (TOTP) to provide additional protection for administrative accounts.", bullet))
    story.append(Paragraph("• Automated email and webhook notifications to alert risk owners when remediation target dates approach.", bullet))
    story.append(Paragraph("• Role-specific mobile dashboards allowing department managers to review and approve treatment actions remotely.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 23 (Body Page 13): BIBLIOGRAPHY & REFERENCES
    # =========================================================================
    story.append(Paragraph("<b>BIBLIOGRAPHY & REFERENCES</b>", ParagraphStyle('BibHead', fontName=font_bold, fontSize=14, alignment=1, spaceBefore=10, spaceAfter=20)))

    bib_items = [
        "[1] National Institute of Standards and Technology (NIST), \"Guide for Conducting Risk Assessments,\" NIST Special Publication 800-30 Revision 1, U.S. Department of Commerce, 2012.",
        "[2] International Organization for Standardization (ISO), \"Information security, cybersecurity and privacy protection — Information security risk management,\" ISO/IEC 27005:2022, Geneva, Switzerland, 2022.",
        "[3] Python Software Foundation, \"The Python Standard Library Documentation — http.server, sqlite3, hashlib, and secrets,\" Python 3.11 Documentation, https://docs.python.org/3/library/.",
        "[4] SQLite Consortium, \"SQLite Database Engine Documentation — Foreign Key Support and ACID Transactions,\" https://www.sqlite.org/docs.html.",
        "[5] Center for Internet Security (CIS), \"CIS Critical Security Controls Version 8,\" Center for Internet Security, 2021.",
        "[6] OWASP Foundation, \"OWASP Top 10 Information Security Best Practices,\" https://owasp.org/www-project-top-ten/.",
        "[7] Mozilla Developer Network (MDN), \"Web APIs and Modern JavaScript (ES6+) Standards,\" https://developer.mozilla.org/.",
        "[8] Silver Oak College of Computer Application, \"MCA Minor Project Guidelines and Academic Standards,\" Silver Oak University, Ahmedabad, 2026.",
    ]
    for item in bib_items:
        story.append(Paragraph(item, ParagraphStyle('BibItem', parent=body, leftIndent=20, firstLineIndent=-20, spaceAfter=8)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 24 (Body Page 14): APPENDICES — Appendix A Review 1 Evaluation Sheet
    # =========================================================================
    story.append(Paragraph("<b>APPENDICES</b>", ParagraphStyle('AppHead', fontName=font_bold, fontSize=14, alignment=1, spaceBefore=10, spaceAfter=18)))
    story.append(Paragraph("<b>Appendix A Review 1 — Scanned Copy</b>", ParagraphStyle('AppA', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=12)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 1 evaluation sheet here.]</i>", ParagraphStyle('AppANote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 14))

    # Academic Evaluation Rubric Table for Review 1
    rev1_data = [
        [Paragraph("<b>Parameter</b>", table_header), Paragraph("<b>Max Marks</b>", table_header), Paragraph("<b>Marks Awarded</b>", table_header)],
        [Paragraph("Problem Identification & Feasibility Study", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("Literature Review & System Requirement Analysis", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("Project Planning & Methodology", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("<b>Total Score (Review 1)</b>", table_header), Paragraph("<b>30</b>", table_header), Paragraph("&nbsp;", table_header)],
    ]
    t_rev1 = Table(rev1_data, colWidths=[280, 100, 120])
    t_rev1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rev1)
    story.append(Spacer(1, 50))

    rev1_sig = [
        [
            Paragraph("<b>Guide Signature:</b> ___________________", ParagraphStyle('R1G', fontName=font_name, fontSize=10)),
            Paragraph("<b>Examiner Signature:</b> ___________________", ParagraphStyle('R1E', fontName=font_name, fontSize=10, alignment=2))
        ]
    ]
    t_r1_sig = Table(rev1_sig, colWidths=[250, 250])
    t_r1_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_r1_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 25 (Body Page 15): Appendix B Review 2 Evaluation Sheet
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Appendix B Review 2 — Scanned Copy</b>", ParagraphStyle('AppB', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=12)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 2 evaluation sheet here.]</i>", ParagraphStyle('AppBNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 14))

    rev2_data = [
        [Paragraph("<b>Parameter</b>", table_header), Paragraph("<b>Max Marks</b>", table_header), Paragraph("<b>Marks Awarded</b>", table_header)],
        [Paragraph("System Architecture & Data Flow Diagrams (DFDs)", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("Relational Database Design & Schema Integrity", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("UML Modeling (Use Case, Class, Sequence Diagrams)", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("<b>Total Score (Review 2)</b>", table_header), Paragraph("<b>30</b>", table_header), Paragraph("&nbsp;", table_header)],
    ]
    t_rev2 = Table(rev2_data, colWidths=[280, 100, 120])
    t_rev2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rev2)
    story.append(Spacer(1, 50))

    rev2_sig = [
        [
            Paragraph("<b>Guide Signature:</b> ___________________", ParagraphStyle('R2G', fontName=font_name, fontSize=10)),
            Paragraph("<b>Examiner Signature:</b> ___________________", ParagraphStyle('R2E', fontName=font_name, fontSize=10, alignment=2))
        ]
    ]
    t_r2_sig = Table(rev2_sig, colWidths=[250, 250])
    t_r2_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_r2_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 26 (Body Page 16): Appendix C Review 3 Evaluation Sheet
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Appendix C Review 3 — Scanned Copy</b>", ParagraphStyle('AppC', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=12)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 3 evaluation sheet here.]</i>", ParagraphStyle('AppCNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 14))

    rev3_data = [
        [Paragraph("<b>Parameter</b>", table_header), Paragraph("<b>Max Marks</b>", table_header), Paragraph("<b>Marks Awarded</b>", table_header)],
        [Paragraph("Module Implementation & Backend Logic", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("User Interface Usability & Dashboard Design", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("Coding Standards, Security & Code Quality", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("<b>Total Score (Review 3)</b>", table_header), Paragraph("<b>30</b>", table_header), Paragraph("&nbsp;", table_header)],
    ]
    t_rev3 = Table(rev3_data, colWidths=[280, 100, 120])
    t_rev3.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rev3)
    story.append(Spacer(1, 50))

    rev3_sig = [
        [
            Paragraph("<b>Guide Signature:</b> ___________________", ParagraphStyle('R3G', fontName=font_name, fontSize=10)),
            Paragraph("<b>Examiner Signature:</b> ___________________", ParagraphStyle('R3E', fontName=font_name, fontSize=10, alignment=2))
        ]
    ]
    t_r3_sig = Table(rev3_sig, colWidths=[250, 250])
    t_r3_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_r3_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 27 (Body Page 17): Appendix D Review 4 Evaluation Sheet
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Appendix D Review 4 — Scanned Copy</b>", ParagraphStyle('AppD', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=12)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 4 evaluation sheet here.]</i>", ParagraphStyle('AppDNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 14))

    rev4_data = [
        [Paragraph("<b>Parameter</b>", table_header), Paragraph("<b>Max Marks</b>", table_header), Paragraph("<b>Marks Awarded</b>", table_header)],
        [Paragraph("Testing Strategy & Automated Test Case Execution", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("Final Project Demonstration & Q&A Defense", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("Documentation Quality & Academic Report Compliance", table_cell), Paragraph("10", table_cell), Paragraph("&nbsp;", table_cell)],
        [Paragraph("<b>Total Score (Final Review 4)</b>", table_header), Paragraph("<b>30</b>", table_header), Paragraph("&nbsp;", table_header)],
    ]
    t_rev4 = Table(rev4_data, colWidths=[280, 100, 120])
    t_rev4.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_rev4)
    story.append(Spacer(1, 50))

    rev4_sig = [
        [
            Paragraph("<b>Internal Guide Signature:</b> ___________________", ParagraphStyle('R4G', fontName=font_name, fontSize=10)),
            Paragraph("<b>External Examiner Signature:</b> ___________________", ParagraphStyle('R4E', fontName=font_name, fontSize=10, alignment=2))
        ]
    ]
    t_r4_sig = Table(rev4_sig, colWidths=[250, 250])
    t_r4_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_r4_sig)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 28 (Body Page 18): PUBLICATION / PATENT / RESEARCH OUTPUT
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>PUBLICATION / PATENT / RESEARCH OUTPUT</b>", ParagraphStyle('PubHead', fontName=font_bold, fontSize=13, alignment=1, spaceAfter=20)))
    story.append(Paragraph("(This section is optional and applicable only if the student has published a research paper, filed a patent, or produced any other research output based on this project.)", ParagraphStyle('PubNote', parent=body, alignment=1, fontName=font_italic)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>[Insert scanned copy of the publication certificate / acceptance letter / patent filing receipt here.]</i>", ParagraphStyle('PubPlaceholder', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    # Build document
    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Academic University Project Report generated successfully at: {output_pdf}")


if __name__ == "__main__":
    build_academic_pdf()
