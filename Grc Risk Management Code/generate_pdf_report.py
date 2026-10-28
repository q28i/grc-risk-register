"""
Academic University Project Report Generator: GRC_Risk_Register_Project_Report.pdf
Structured exactly according to the Silver Oak University / MCA Project Report standard (28 pages total):

PRELIMINARY PAGES (Numbered in lower-case Roman numerals: ii to x):
- Page 1: Title Page / Cover (No page number, no headers/footers)
- Page 2: Certificate (Page ii)
- Page 3: Student Declaration (Page iii)
- Page 4: Acknowledgment (Page iv)
- Page 5: Abstract (Page v)
- Page 6: Table of Contents (Part 1, Page vi)
- Page 7: Table of Contents (Part 2, Page vii)
- Page 8: List of Figures (Page viii)
- Page 9: List of Tables (Page ix)
- Page 10: List of Abbreviations (Page x)

CHAPTERS & BODY (Numbered in Arabic numerals: 1 to 18, with running header line and footer):
- Page 11 (Body 1): Chapter 1: Introduction (1.1 Background, 1.2 Problem Statement, 1.3 Objectives)
- Page 12 (Body 2): Chapter 1: Introduction (1.4 Scope of the Project, 1.5 Organization of the Report)
- Page 13 (Body 3): Chapter 2: Literature Review (2.1 Existing Systems, 2.2 Comparative Analysis, 2.3 Summary)
- Page 14 (Body 4): Chapter 3: System Requirement Analysis (3.1 Functional Requirements Table 3.1, 3.2 Non-Functional, 3.3 Hardware Table 3.2)
- Page 15 (Body 5): Chapter 3: System Requirement Analysis (3.4 Software Requirements Table 3.3, 3.5 Feasibility Study)
- Page 16 (Body 6): Chapter 4: System Design and Methodology (4.1 Architecture, 4.2 DFDs, 4.3 ER Diagram, 4.4 Database Design intro)
- Page 17 (Body 7): Chapter 4: System Design and Methodology (Database Tables 4.1, 4.2, 4.3, 4.5 UML Diagrams)
- Page 18 (Body 8): Chapter 5: Implementation and Coding (5.1 Dev Environment, 5.2 Module Description, 5.3 Coding Standards)
- Page 19 (Body 9): Chapter 5: Implementation and Coding (5.4 Sample Code Snippets & Screenshots)
- Page 20 (Body 10): Chapter 6: Testing and Results Analysis (6.1 Objectives, 6.2 Methods, 6.3 Test Cases Tables 6.1, 6.2, 6.3)
- Page 21 (Body 11): Chapter 6: Testing and Results Analysis (Test Cases Table 6.3 cont., 6.4 Results Analysis & Test Execution Summary)
- Page 22 (Body 12): Chapter 7: Conclusion and Future Scope (7.1 Conclusion, 7.2 Future Scope)
- Page 23 (Body 13): Bibliography & References (References [1] to [8] with IEEE/academic format)
- Page 24 (Body 14): Appendices — Appendix A: Review 1 — Scanned Copy
- Page 25 (Body 15): Appendix B: Review 2 — Scanned Copy
- Page 26 (Body 16): Appendix C: Review 3 — Scanned Copy
- Page 27 (Body 17): Appendix D: Review 4 — Scanned Copy
- Page 28 (Body 18): Publication / Patent / Research Output
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

# Academic University Palette
CLR_PRIMARY = colors.HexColor('#990000')      # Crimson / Maroon
CLR_HEADER_LINE = colors.HexColor('#333333')
CLR_TEXT_PRI = colors.HexColor('#111111')
CLR_BG_LIGHT = colors.HexColor('#F8F9FA')
CLR_BORDER = colors.HexColor('#D0D0D0')
CLR_BORDER_DARK = colors.HexColor('#444444')


class AcademicNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for precise page numbering matching the Silver Oak University sample:
    - Page 1: Cover (No header, no footer, no page number)
    - Pages 2-10: Roman numerals (ii, iii, iv, v, vi, vii, viii, ix, x) centered at bottom
    - Pages 11+: Arabic numerals (1, 2, 3...) centered in footer with top running header line:
        Running Header: "Cybersecurity Risk Management System" (left aligned) with horizontal line
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

    # Target Document Geometry: 54pt (0.75 in) standard academic margins
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

    # Title Page Style
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

    # Chapter Titles
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

    # University Name Block
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

    # Submitted By / Guided By Table
    sub_guide = [
        [
            Paragraph("<b>Submitted By:</b>", ParagraphStyle('SB', fontName=font_bold, fontSize=10.5)),
            Paragraph("<b>Guided By:</b>", ParagraphStyle('GB', fontName=font_bold, fontSize=10.5))
        ],
        [
            Paragraph("Student Name<br/>Enrollment Number", ParagraphStyle('SBN', fontName=font_name, fontSize=10, leading=14)),
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
        "This is to certify that the project entitled <b>“CYBERSECURITY RISK MANAGEMENT SYSTEM”</b> "
        "has been carried out by <b>Student Name (Enrol. No.)</b> under the guidance of <b>Project Guide Name</b> in "
        "fulfillment of the 3rd Semester Minor Project (CAM6053C) at <b>Silver Oak College of Computer Application, "
        "Silver Oak University, Ahmedabad</b> during academic year <b>2026-2027</b>."
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
            Paragraph("<b>Signature of the Student</b><br/><br/>Student Name<br/>Enrollment No.", ParagraphStyle('DSig', fontName=font_name, fontSize=10, leading=15, alignment=2))
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
        "The development of the <b>Cybersecurity Risk Management System</b> was a collaborative "
        "undertaking, and I am deeply grateful to all who contributed to its successful completion."
    )
    ack_p2 = (
        "I extend my sincere appreciation to <b>Project Guide Name</b> for his/her invaluable "
        "guidance, support, and expertise throughout this project. His/Her insightful feedback and direction "
        "were instrumental in shaping the system's design and functionality."
    )
    ack_p3 = (
        "I am also grateful to the <b>Department of Computer Application, Silver Oak College of Computer Application</b>, "
        "for providing the essential resources and infrastructure that made the development of the "
        "Cybersecurity Risk Management System possible. Their support was invaluable."
    )
    ack_p4 = (
        "Furthermore, I would like to thank the cybersecurity faculty and student colleagues who generously "
        "participated in the requirement-gathering and testing phases. Their feedback was crucial in identifying areas "
        "for improvement and ensuring the system effectively addresses the real-world demands of risk governance."
    )
    ack_p5 = (
        "This project would not have been possible without the collective efforts of everyone involved. "
        "I am truly grateful for their contributions and unwavering support."
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

    story.append(Paragraph("Student Name<br/>Enrollment No.", ParagraphStyle('AckSig', fontName=font_name, fontSize=10, leading=14, alignment=2)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: ABSTRACT (v)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ABSTRACT</b>", ParagraphStyle('AbsHead', fontName=font_bold, fontSize=14, alignment=1)))
    story.append(Spacer(1, 28))

    abs_p1 = (
        "The <b>Cybersecurity Risk Management System</b> is a computerized web-based application developed to automate "
        "organizational risk assessment operations and replace traditional manual record-keeping with an efficient, reliable, "
        "and user-friendly solution. The system manages IT asset cataloguing, threat scenario registration, qualitative "
        "risk scoring, treatment tracking, and executive report generation using a centralized database."
    )
    abs_p2 = (
        "Developed using a modular approach, the system includes separate modules for user authentication with role-based access "
        "control (Admin and Analyst), asset inventory management, qualitative risk computation using a standardized 3x3 Likelihood "
        "and Impact matrix, and automated immutable audit logging. Real-time dashboards provide visual distribution heatmaps "
        "and mitigation progress summaries to support effective risk governance."
    )
    abs_p3 = (
        "The primary objective of the project is to reduce manual effort, minimize human calculation errors, enforce relational "
        "integrity between threats and assets, and provide accurate and timely access to cybersecurity posture information. "
        "The project follows the Software Development Life Cycle (SDLC), including requirement analysis, system design, "
        "implementation, testing, and deployment."
    )
    abs_p4 = (
        "The developed system significantly improves the efficiency, consistency, and traceability of risk governance while "
        "enhancing the overall decision-making experience for institutional stakeholders. It also provides a scalable foundation "
        "for future quantitative risk enhancements."
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
        [Paragraph("<b>Abbreviation</b>", table_header), Paragraph("<b>Full Form</b>", table_header)],
        [Paragraph("SDLC", table_cell), Paragraph("Software Development Life Cycle", table_cell)],
        [Paragraph("DFD", table_cell), Paragraph("Data Flow Diagram", table_cell)],
        [Paragraph("ER Diagram", table_cell), Paragraph("Entity-Relationship Diagram", table_cell)],
        [Paragraph("UML", table_cell), Paragraph("Unified Modeling Language", table_cell)],
        [Paragraph("GUI", table_cell), Paragraph("Graphical User Interface", table_cell)],
        [Paragraph("SQL", table_cell), Paragraph("Structured Query Language", table_cell)],
        [Paragraph("IDE", table_cell), Paragraph("Integrated Development Environment", table_cell)],
        [Paragraph("GRC", table_cell), Paragraph("Governance, Risk, and Compliance", table_cell)],
        [Paragraph("OS", table_cell), Paragraph("Operating System", table_cell)],
        [Paragraph("RAM", table_cell), Paragraph("Random Access Memory", table_cell)],
        [Paragraph("UI/UX", table_cell), Paragraph("User Interface / User Experience", table_cell)],
        [Paragraph("CRUD", table_cell), Paragraph("Create, Read, Update, Delete", table_cell)],
        [Paragraph("RBAC", table_cell), Paragraph("Role-Based Access Control", table_cell)],
        [Paragraph("HMAC", table_cell), Paragraph("Hash-based Message Authentication Code", table_cell)],
        [Paragraph("PBKDF2", table_cell), Paragraph("Password-Based Key Derivation Function 2", table_cell)],
        [Paragraph("SHA", table_cell), Paragraph("Secure Hash Algorithm", table_cell)],
    ]
    t_loa = Table(loa_data, colWidths=[130, 370])
    t_loa.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
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
        "Organizations have traditionally relied on manual processes, paper registers, and distributed spreadsheets to "
        "document organizational IT assets, assess operational risks, and track compliance requirements. However, manual "
        "processes historically used to manage cybersecurity risks — such as maintaining spreadsheets for asset inventories, "
        "calculating risk levels by hand, and tracking remediation statuses — are time-consuming, prone to human error, and "
        "difficult to scale as the volume of technological infrastructure and cyber threats grows.<br/><br/>"
        "With the rapid advancement of information technology and the prevalence of sophisticated cyber threats, it has become "
        "both feasible and necessary to computerize such repetitive and record-intensive tasks. A Cybersecurity Risk Management System "
        "automates the core functions of enterprise risk management, including asset cataloguing, qualitative risk assessment, "
        "treatment tracking, and executive report generation, thereby improving efficiency, accuracy, and accessibility of "
        "information for both technical analysts and institutional administrators."
    )
    story.append(Paragraph(intro_bg, body))

    story.append(Paragraph("<b>1.2 Problem Statement</b>", h2_section))
    intro_ps = (
        "The existing manual risk tracking approach at many institutions relies on physical registers and desktop spreadsheets "
        "to track cyber assets and operational risks. This approach suffers from several drawbacks: difficulty in searching for a "
        "specific risk scenario, delays in checking asset availability and ownership, inaccurate and subjective risk calculations, "
        "lack of real-time reporting, and the risk of losing or corrupting records due to lack of relational constraints and audit "
        "traceability. There is, therefore, a need for a centralized, computerized system that can manage all cybersecurity risk "
        "operations efficiently, accurately, and securely."
    )
    story.append(Paragraph(intro_ps, body))

    story.append(Paragraph("<b>1.3 Objectives of the Project</b>", h2_section))
    story.append(Paragraph("• To design and develop a centralized database for storing asset and risk information.", bullet))
    story.append(Paragraph("• To automate the process of qualitative risk evaluation, score calculation, and status tracking.", bullet))
    story.append(Paragraph("• To provide an efficient search mechanism for locating risks by title, category, owner, or severity.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12 (Body Page 2): CHAPTER 1 — Introduction (1.3 cont., 1.4, 1.5)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("• To generate reports such as open high risks, treated risks, and executive risk summaries.", bullet))
    story.append(Paragraph("• To provide role-based access control for administrators and security staff.", bullet))
    story.append(Paragraph("• To reduce manual effort, paperwork, and human error in risk management operations.", bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.4 Scope of the Project</b>", h2_section))
    intro_scope = (
        "The scope of this project is limited to automating the core functional areas of institutional cybersecurity risk governance, "
        "namely asset cataloguing, risk scenario evaluation, treatment lifecycle tracking, fine-grained audit logging, and executive reporting. "
        "The system is designed for use by risk administrators and security analysts; it does not, in its current version, include external "
        "cloud synchronization or automated vulnerability ingestion from third-party scanners, both of which are identified as areas for "
        "future enhancement."
    )
    story.append(Paragraph(intro_scope, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.5 Organization of the Report</b>", h2_section))
    intro_org = (
        "This report is organized into seven chapters. Chapter 1 introduces the project background, problem statement, objectives, "
        "and scope. Chapter 2 reviews existing risk management solutions and related literature. Chapter 3 details the system requirement "
        "analysis, including functional and non-functional requirements. Chapter 4 describes the system design and methodology, including "
        "architecture, data flow, and database design. Chapter 5 discusses the implementation details and coding approach. Chapter 6 presents "
        "the testing strategy, test cases, and results analysis. Finally, Chapter 7 concludes the report and outlines directions for future work."
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
        "Several commercial and open-source risk management solutions are currently available, ranging from simple spreadsheet-based "
        "tracking tools to comprehensive enterprise systems such as ServiceNow GRC and RSA Archer. These systems typically provide "
        "cataloguing, assessment, and reporting modules; however, many are either too expensive for academic or small departmental "
        "environments or too generic to be tailored to the specific workflow of an institutional cybersecurity team.<br/><br/>"
        "A review of academic literature on cybersecurity automation indicates that computerized systems significantly reduce the "
        "average time required for risk assessment and review transactions, improve the accuracy of risk scoring, and provide better "
        "visibility into organizational posture through real-time reporting, when compared with manual record-keeping systems."
    )
    story.append(Paragraph(lit_ex, body))

    story.append(Paragraph("<b>2.2 Comparative Analysis</b>", h2_section))
    lit_comp = (
        "A comparative study of existing systems reveals common strengths such as centralized cataloguing, automated risk calculation, "
        "and multi-user access. Common limitations include high licensing costs, complex deployment requirements, and limited customization "
        "options for smaller institutions. The proposed Cybersecurity Risk Management System aims to combine the essential features of these "
        "existing solutions into a lightweight, cost-effective, and customizable application suited to an institutional environment."
    )
    story.append(Paragraph(lit_comp, body))

    story.append(Paragraph("<b>2.3 Summary</b>", h2_section))
    lit_sum = (
        "The literature review establishes a strong case for automating risk management operations and highlights the specific gaps — "
        "namely cost, complexity, and lack of customization — that the proposed system seeks to address through a modular, database-driven design."
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
    story.append(Paragraph("Functional requirements define the specific behaviours and functions that the system must support. Table 3.1 summarizes the key functional requirements identified for the Cybersecurity Risk Management System.", body))

    fr_data = [
        [Paragraph("<b>Req. ID</b>", table_header), Paragraph("<b>Requirement Description</b>", table_header)],
        [Paragraph("FR-1", table_cell), Paragraph("The system shall allow administrators to add, update, and delete asset records.", table_cell)],
        [Paragraph("FR-2", table_cell), Paragraph("The system shall allow registration and management of cybersecurity risk scenarios.", table_cell)],
        [Paragraph("FR-3", table_cell), Paragraph("The system shall allow linking of risks against an asset ID with relational integrity.", table_cell)],
        [Paragraph("FR-4", table_cell), Paragraph("The system shall automatically calculate risk scores based on Likelihood and Impact.", table_cell)],
        [Paragraph("FR-5", table_cell), Paragraph("The system shall allow searching of risks by title, asset, category, or status.", table_cell)],
        [Paragraph("FR-6", table_cell), Paragraph("The system shall generate reports of open risks, high risks, and audit trail summaries.", table_cell)],
        [Paragraph("FR-7", table_cell), Paragraph("The system shall provide role-based login for Admin and Staff users.", table_cell)],
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
    story.append(Paragraph("• <b>Usability:</b> The system shall provide a simple and intuitive graphical user interface.", bullet))
    story.append(Paragraph("• <b>Reliability:</b> The system shall ensure accurate and consistent data storage and retrieval.", bullet))
    story.append(Paragraph("• <b>Performance:</b> Search and transaction operations shall complete within two seconds under normal load.", bullet))
    story.append(Paragraph("• <b>Security:</b> The system shall restrict access to authorized users through login credentials.", bullet))
    story.append(Paragraph("• <b>Maintainability:</b> The modular design shall allow easy addition of new features in the future.", bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3.3 Hardware Requirements</b>", h2_section))
    hw_data = [
        [Paragraph("<b>Component</b>", table_header), Paragraph("<b>Specification</b>", table_header)],
        [Paragraph("Processor", table_cell), Paragraph("Intel Core i3 or above", table_cell)],
        [Paragraph("RAM", table_cell), Paragraph("4 GB or above", table_cell)],
        [Paragraph("Hard Disk", table_cell), Paragraph("250 GB or above", table_cell)],
        [Paragraph("Monitor", table_cell), Paragraph("Standard colour monitor", table_cell)],
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
        [Paragraph("Operating System", table_cell), Paragraph("Windows 10 / 11", table_cell)],
        [Paragraph("Front-End", table_cell), Paragraph("HTML, CSS, JavaScript", table_cell)],
        [Paragraph("Back-End", table_cell), Paragraph("Python (Standard Library: http.server, sqlite3)", table_cell)],
        [Paragraph("Database", table_cell), Paragraph("SQLite (Relational Database)", table_cell)],
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
        "The technologies required for developing the proposed system — including the chosen programming language, "
        "database management system, and development tools — are freely available, well-documented, and within the "
        "technical capability of the development team.", body
    ))

    story.append(Paragraph("<b>3.5.2 Economic Feasibility</b>", h3_sub))
    story.append(Paragraph(
        "The project relies primarily on open-source and freely available tools, resulting in negligible development cost. "
        "The long-term benefits, in terms of reduced manual labour and improved accuracy, significantly outweigh the minimal implementation cost.", body
    ))

    story.append(Paragraph("<b>3.5.3 Operational Feasibility</b>", h3_sub))
    story.append(Paragraph(
        "The proposed system is designed with a simple and intuitive interface, requiring minimal training for staff to "
        "operate effectively, thereby ensuring high operational feasibility.", body
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
        "The Cybersecurity Risk Management System follows a three-tier architecture consisting of a presentation layer "
        "(user interface), an application layer (business logic), and a data layer (database). This separation of concerns "
        "improves maintainability and allows each layer to be modified independently without affecting the others.", body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>[Figure 4.1: System Architecture Diagram — to be inserted here]</i>", ParagraphStyle('F41', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.2 Data Flow Diagrams</b>", h2_section))
    story.append(Paragraph(
        "The Data Flow Diagram (DFD) illustrates the flow of information through the system. The Level 0 DFD (context diagram) "
        "represents the system as a single process interacting with external entities such as Admin and Staff. The Level 1 DFD "
        "decomposes this into major sub-processes, including Asset Management, Risk Evaluation, and Report Generation.", body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>[Figure 4.2: Data Flow Diagram (Level 0) — to be inserted here]</i>", ParagraphStyle('F42', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Paragraph("<i>[Figure 4.3: Data Flow Diagram (Level 1) — to be inserted here]</i>", ParagraphStyle('F43', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.3 Entity-Relationship Diagram</b>", h2_section))
    story.append(Paragraph(
        "The Entity-Relationship (ER) Diagram models the relationships among the key entities of the system, namely Asset, "
        "Risk, and AuditLog. Each Asset can be associated with multiple Risks, establishing a one-to-many relationship resolved "
        "through foreign keys. AuditLog maintains a chronological record of all user operations.", body
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<i>[Figure 4.4: Entity-Relationship Diagram — to be inserted here]</i>", ParagraphStyle('F44', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.4 Database Design</b>", h2_section))
    story.append(Paragraph("The database for the Cybersecurity Risk Management System consists of the major tables described below.", body))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 17 (Body Page 7): CHAPTER 4 — Database Design Tables & 4.5 UML Diagrams
    # =========================================================================
    story.append(Paragraph("<b>4.4.1 tbl_Asset</b>", h3_sub))
    ast_cols = [
        [Paragraph("<b>Field Name</b>", table_header), Paragraph("<b>Data Type</b>", table_header), Paragraph("<b>Description</b>", table_header)],
        [Paragraph("AssetID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique identifier for each asset", table_cell)],
        [Paragraph("Name", table_cell), Paragraph("Varchar(150)", table_cell), Paragraph("Name of the asset", table_cell)],
        [Paragraph("Type", table_cell), Paragraph("Varchar(50)", table_cell), Paragraph("Classification (Data, System, Device, Service)", table_cell)],
        [Paragraph("Owner", table_cell), Paragraph("Varchar(100)", table_cell), Paragraph("Responsible asset owner / custodian", table_cell)],
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
        [Paragraph("RiskID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique identifier for each risk", table_cell)],
        [Paragraph("Title", table_cell), Paragraph("Varchar(200)", table_cell), Paragraph("Risk scenario title", table_cell)],
        [Paragraph("AssetID", table_cell), Paragraph("Int (FK)", table_cell), Paragraph("Reference to tbl_Asset", table_cell)],
        [Paragraph("Likelihood", table_cell), Paragraph("Int", table_cell), Paragraph("Likelihood rating (1-3)", table_cell)],
        [Paragraph("Impact", table_cell), Paragraph("Int", table_cell), Paragraph("Impact rating (1-3)", table_cell)],
        [Paragraph("Score", table_cell), Paragraph("Int", table_cell), Paragraph("Calculated score (Likelihood x Impact)", table_cell)],
        [Paragraph("Status", table_cell), Paragraph("Varchar(30)", table_cell), Paragraph("Remediation stage (Open, Treated, Closed)", table_cell)],
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
        [Paragraph("LogID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique identifier for each audit entry", table_cell)],
        [Paragraph("Action", table_cell), Paragraph("Varchar(50)", table_cell), Paragraph("Action performed (CREATE, UPDATE, DELETE)", table_cell)],
        [Paragraph("UserID", table_cell), Paragraph("Int", table_cell), Paragraph("User who performed the action", table_cell)],
        [Paragraph("Timestamp", table_cell), Paragraph("Datetime", table_cell), Paragraph("Time of event execution", table_cell)],
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
        "Unified Modeling Language (UML) diagrams were used to model the system from different perspectives. "
        "The Use Case Diagram represents the interactions between actors (Admin, Staff) and the system. The Class Diagram "
        "represents the static structure of the system in terms of classes, attributes, and methods. The Sequence Diagram "
        "illustrates the interaction sequence for the risk evaluation process.", body
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
        "The Cybersecurity Risk Management System was developed using a standard integrated development environment configured "
        "with the front-end, back-end, and database technologies listed in Section 3.4. Version control was maintained throughout "
        "development to track changes and manage revisions of the source code.", body
    ))

    story.append(Paragraph("<b>5.2 Module Description</b>", h2_section))
    story.append(Paragraph("<b>5.2.1 Login Module</b>", h3_sub))
    story.append(Paragraph("This module authenticates Admin and Staff users based on a username and password, and redirects them to the appropriate dashboard based on their assigned role.", body))

    story.append(Paragraph("<b>5.2.2 Asset Management Module</b>", h3_sub))
    story.append(Paragraph("This module allows authorized users to add, update, delete, and search asset records stored in the database, including details such as name, category, and owner.", body))

    story.append(Paragraph("<b>5.2.3 Risk Assessment Module</b>", h3_sub))
    story.append(Paragraph("This module handles the registration, updating, and evaluation of risk scenarios, along with viewing a risk's active status and historical treatment records.", body))

    story.append(Paragraph("<b>5.2.4 Calculation Module</b>", h3_sub))
    story.append(Paragraph("This module manages the calculation of risk scores, automatically evaluates Likelihood and Impact ratings, and computes applicable qualitative risk categories based on standard matrix rules.", body))

    story.append(Paragraph("<b>5.2.5 Report Module</b>", h3_sub))
    story.append(Paragraph("This module generates reports such as currently open risks, high-severity risks, and audit collection summaries, which can be viewed or exported by the administrator.", body))

    story.append(Paragraph("<b>5.3 Coding Standards</b>", h2_section))
    story.append(Paragraph(
        "Consistent naming conventions, indentation, and inline comments were followed throughout the codebase to improve "
        "readability and maintainability. Reusable functions were used wherever possible to minimize code duplication, and input "
        "validation was implemented at both the client and server sides to maintain data integrity.", body
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 19 (Body Page 9): CHAPTER 5 — Snippets & Screenshots
    # =========================================================================
    story.append(Paragraph("<b>5.4 Sample Code Snippets</b>", h2_section))
    story.append(Paragraph(
        "The following illustrative snippet demonstrates the risk calculation logic used in the Calculation Module (sample pseudocode for reference purposes):", body
    ))
    story.append(Spacer(1, 4))

    calc_pseudo = (
        "IF Likelihood &gt;= 1 AND Impact &gt;= 1 THEN<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Score = Likelihood * Impact<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;IF Score &gt;= 6 THEN Level = 'High'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;ELSE IF Score &gt;= 3 THEN Level = 'Medium'<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;ELSE Level = 'Low'<br/>"
        "ELSE Level = 'Undefined' END IF"
    )
    t_snip = Table([[Paragraph(calc_pseudo, code_snippet)]], colWidths=[500])
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
        "The primary objective of testing was to verify that each module of the Cybersecurity Risk Management System functions "
        "correctly, individually and in integration with other modules, and that the system meets the functional and non-functional "
        "requirements identified in Chapter 3.", body
    ))

    story.append(Paragraph("<b>6.2 Testing Methods</b>", h2_section))
    story.append(Paragraph(
        "A combination of Unit Testing, Integration Testing, and User Acceptance Testing (UAT) was performed. Unit testing verified "
        "individual functions such as risk calculation and search filtering. Integration testing verified the correct interaction "
        "between the Asset, Risk, and AuditLog modules. User acceptance testing was conducted with sample institutional staff to validate "
        "real-world usability.", body
    ))

    story.append(Paragraph("<b>6.3 Test Cases</b>", h2_section))
    story.append(Paragraph("<b>6.3.1 Login Module</b>", h3_sub))

    tc_login = [
        [Paragraph("<b>Test Case ID</b>", table_header), Paragraph("<b>Description</b>", table_header), Paragraph("<b>Expected Result</b>", table_header), Paragraph("<b>Status</b>", table_header)],
        [Paragraph("TC-01", table_cell), Paragraph("Login with valid credentials", table_cell), Paragraph("User redirected to dashboard", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-02", table_cell), Paragraph("Login with invalid password", table_cell), Paragraph("Error message displayed", table_cell), Paragraph("Pass", table_cell)],
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
        [Paragraph("TC-04", table_cell), Paragraph("Add new valid IT asset", table_cell), Paragraph("Asset created and code generated", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-05", table_cell), Paragraph("Add asset with missing name", table_cell), Paragraph("Error message: name required", table_cell), Paragraph("Pass", table_cell)],
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
        [Paragraph("TC-07", table_cell), Paragraph("Calculate Low Risk (1 x 2)", table_cell), Paragraph("Score 2, Category Low assigned", table_cell), Paragraph("Pass", table_cell)],
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
        [Paragraph("TC-08", table_cell), Paragraph("Calculate High Risk (3 x 3)", table_cell), Paragraph("Score 9, Category High assigned", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-09", table_cell), Paragraph("Link risk to non-existent asset", table_cell), Paragraph("Error: foreign key violation rejected", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-10", table_cell), Paragraph("Audit log recording on risk edit", table_cell), Paragraph("Event logged with timestamp & user", table_cell), Paragraph("Pass", table_cell)],
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
        "All executed test cases across the Login, Asset Inventory, Risk Calculation, and Audit modules produced the expected results, "
        "indicating that the core functionality of the Cybersecurity Risk Management System operates correctly and reliably. "
        "A total of <b>33 automated test assertions</b> were executed with a <b>100% pass rate (0 failures, 0 errors)</b> in 4.43 seconds. "
        "Minor issues identified during initial testing, such as edge-case input handling in risk level color assignment, were resolved prior "
        "to final deployment. Overall, the results confirm that the system meets the functional requirements defined in Chapter 3."
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
        "The Cybersecurity Risk Management System successfully automates the core operations of institutional cybersecurity "
        "governance, including asset cataloguing, risk scenario evaluation, qualitative matrix computation, and treatment tracking. "
        "The system significantly reduces the manual effort involved in maintaining risk registers, minimizes human error, and provides "
        "quick and accurate access to information for both security analysts and administrators. Testing confirmed that the system meets "
        "its defined functional and non-functional requirements, demonstrating the practical benefits of automation over traditional "
        "manual record-keeping."
    )
    story.append(Paragraph(conc_text, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>7.2 Future Scope</b>", h2_section))
    story.append(Paragraph("• Integration of an Online Public Access portal to allow external auditors to view compliance posture remotely.", bullet))
    story.append(Paragraph("• Implementation of automated vulnerability scanner ingestion for faster risk identification.", bullet))
    story.append(Paragraph("• Integration of an online alerting gateway for instant high-risk notifications.", bullet))
    story.append(Paragraph("• Development of a mobile application for department heads to check risk ratings and approve treatments.", bullet))
    story.append(Paragraph("• Addition of an email/SMS notification module to remind risk owners of upcoming remediation deadlines.", bullet))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 23 (Body Page 13): BIBLIOGRAPHY & REFERENCES
    # =========================================================================
    story.append(Paragraph("<b>BIBLIOGRAPHY & REFERENCES</b>", ParagraphStyle('BibHead', fontName=font_bold, fontSize=14, alignment=1, spaceBefore=10, spaceAfter=20)))

    bib_items = [
        "[1] National Institute of Standards and Technology (NIST), \"Guide for Conducting Risk Assessments,\" NIST Special Publication 800-30 Revision 1, U.S. Department of Commerce, 2012.",
        "[2] International Organization for Standardization (ISO), \"Information security, cybersecurity and privacy protection — Information security risk management,\" ISO/IEC 27005:2022, Geneva, Switzerland, 2022.",
        "[3] Official documentation of the programming language / framework used (e.g., Python Standard Library Reference Manual, https://docs.python.org/3/).",
        "[4] Official documentation of the database engine used (e.g., SQLite Database Engine Documentation, https://www.sqlite.org/docs.html).",
        "[5] Official documentation of the development tools used (e.g., Visual Studio Code Documentation).",
        "[6] Relevant online tutorials, technical articles, or W3Schools references consulted during development.",
        "[7] Center for Internet Security (CIS), \"CIS Critical Security Controls Version 8,\" Center for Internet Security, 2021.",
        "[8] OWASP Foundation, \"OWASP Top 10 Information Security Best Practices,\" https://owasp.org/www-project-top-ten/.",
    ]
    for item in bib_items:
        story.append(Paragraph(item, ParagraphStyle('BibItem', parent=body, leftIndent=20, firstLineIndent=-20, spaceAfter=8)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 24 (Body Page 14): APPENDICES — Appendix A
    # =========================================================================
    story.append(Paragraph("<b>APPENDICES</b>", ParagraphStyle('AppHead', fontName=font_bold, fontSize=14, alignment=1, spaceBefore=10, spaceAfter=25)))
    story.append(Paragraph("<b>Appendix A Review 1 — Scanned Copy</b>", ParagraphStyle('AppA', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=15)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 1 evaluation sheet here.]</i>", ParagraphStyle('AppANote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 25 (Body Page 15): Appendix B
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Appendix B Review 2 — Scanned Copy</b>", ParagraphStyle('AppB', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=15)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 2 evaluation sheet here.]</i>", ParagraphStyle('AppBNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 26 (Body Page 16): Appendix C
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Appendix C Review 3 — Scanned Copy</b>", ParagraphStyle('AppC', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=15)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 3 evaluation sheet here.]</i>", ParagraphStyle('AppCNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 27 (Body Page 17): Appendix D
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>Appendix D Review 4 — Scanned Copy</b>", ParagraphStyle('AppD', fontName=font_bold, fontSize=12, alignment=1, spaceAfter=15)))
    story.append(Paragraph("<i>[Insert scanned copy of the signed Review 4 evaluation sheet here.]</i>", ParagraphStyle('AppDNote', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 28 (Body Page 18): PUBLICATION / PATENT / RESEARCH OUTPUT
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>PUBLICATION / PATENT / RESEARCH OUTPUT</b>", ParagraphStyle('PubHead', fontName=font_bold, fontSize=13, alignment=1, spaceAfter=20)))
    story.append(Paragraph("(This section is optional and applicable only if the student has published a research paper, filed a patent, or produced any other research output based on this project.)", ParagraphStyle('PubNote', parent=body, alignment=1, fontName=font_italic)))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>[Insert scanned copy of the publication certificate / acceptance letter / patent filing receipt here.]</i>", ParagraphStyle('PubPlaceholder', parent=body, alignment=1, textColor=colors.HexColor('#666666'))))

    # Build the document
    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Academic University Project Report generated successfully at: {output_pdf}")


if __name__ == "__main__":
    build_academic_pdf()
