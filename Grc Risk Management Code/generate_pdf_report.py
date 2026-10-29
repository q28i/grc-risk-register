"""
Academic University Project Report Generator: GRC_Risk_Register_Project_Report.pdf
Structured exactly as a clone of the Silver Oak University / MCA Project Report sample:

- Exact 28 pages
- Page 1: Cover Page
- Page 2: Certificate (Page ii)
- Page 3: Student Declaration (Page iii)
- Page 4: Acknowledgment (Page iv)
- Page 5: Abstract (Page v)
- Page 6: Table of Contents (Part 1 - Page vi)
- Page 7: Table of Contents (Part 2 - Page vii)
- Page 8: List of Figures (Page viii)
- Page 9: List of Tables (Page ix)
- Page 10: List of Abbreviations (Page x)
- Pages 11-28: Body Chapters 1-7, Bibliography, Appendices A-D, Publication (Pages 1 to 18)

Header & Footer exact specification matching sample:
- Header: Center-aligned "Cybersecurity Risk Management System" (11pt Times-Bold), horizontal line beneath.
- Footer: Horizontal line, Arabic page number centered, followed by "Silver Oak College of Computer Application" (11pt Times-Bold) centered, bottom horizontal rule beneath.
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

# Exact Palette & Styling matching sample PDF
CLR_PRIMARY_RED = colors.HexColor('#CC0000')   # Bright crimson red matching sample: "LIBRARY MANAGEMENT SYSTEM" / red accents
CLR_BLACK = colors.HexColor('#000000')
CLR_GRAY_TEXT = colors.HexColor('#333333')
CLR_BG_LIGHT = colors.HexColor('#EFEFEF')      # Subtle gray for table headers
CLR_BORDER = colors.HexColor('#444444')
CLR_LINE = colors.HexColor('#000000')

STUDENT_NAME = "Tanvi Mishra"
ENROLLMENT_NO = "2504070300016"


class SampleExactCanvas(canvas.Canvas):
    """
    Renders running headers and footers matching the exact visual style of the sample PDF.
    - Page 1: Cover (No header, no footer, no page number)
    - Pages 2-10: Roman numerals centered at bottom (ii, iii, iv, v, vi, vii, viii, ix, x)
    - Pages 11-28:
        Top:
          Centered text: "Cybersecurity Risk Management System" (11pt Times-Bold)
          Black rule underneath across margins
        Bottom:
          Black rule across margins
          Centered: Arabic page number (1, 2, 3...)
          Black rule across margins
          Centered text: "Silver Oak College of Computer Application" (11pt Times-Bold)
          Black rule across margins
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
            self.draw_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_decorations(self, total_pages):
        page_num = self._pageNumber

        # Page 1: Cover Page - completely blank borders/headers
        if page_num == 1:
            return

        self.saveState()

        # Preliminary pages (Pages 2 to 10)
        roman_map = {
            2: "ii", 3: "iii", 4: "iv", 5: "v",
            6: "vi", 7: "vii", 8: "viii", 9: "ix", 10: "x"
        }

        if page_num in roman_map:
            self.setFont("Times-Roman", 11)
            self.setFillColor(CLR_BLACK)
            self.drawCentredString(PAGE_W / 2.0, 36, roman_map[page_num])
            self.restoreState()
            return

        # Chapter body pages (Pages 11 onwards -> 1 to 18)
        arabic_num = page_num - 10

        # --- Running Top Header ---
        self.setFont("Times-Bold", 11)
        self.setFillColor(CLR_BLACK)
        self.drawCentredString(PAGE_W / 2.0, PAGE_H - 36, "Cybersecurity Risk Management System")
        self.setStrokeColor(CLR_LINE)
        self.setLineWidth(1)
        self.line(54, PAGE_H - 44, PAGE_W - 54, PAGE_H - 44)

        # --- Running Bottom Footer ---
        # Rule above page number
        self.line(54, 58, PAGE_W - 54, 58)
        self.setFont("Times-Bold", 11)
        self.drawCentredString(PAGE_W / 2.0, 64, str(arabic_num))
        # Rule between page number and college name
        self.line(54, 52, PAGE_W - 54, 52)
        self.setFont("Times-Bold", 11)
        self.drawCentredString(PAGE_W / 2.0, 38, "Silver Oak College of Computer Application")
        # Rule at the very bottom
        self.line(54, 30, PAGE_W - 54, 30)

        self.restoreState()


def build_academic_pdf():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_pdf = os.path.join(root_dir, "GRC_Risk_Register_Project_Report.pdf")
    media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets_media")

    # Document Geometry: standard margins
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Font Families matching Sample PDF exactly: Times-Roman, Times-Bold, Times-Italic
    f_roman = 'Times-Roman'
    f_bold = 'Times-Bold'
    f_italic = 'Times-Italic'

    # Styles
    cover_label = ParagraphStyle(
        'CoverLabel',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=12,
        leading=16,
        textColor=CLR_BLACK,
        alignment=1,
        spaceAfter=15
    )

    cover_title_red = ParagraphStyle(
        'CoverTitleRed',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=16,
        leading=21,
        textColor=CLR_PRIMARY_RED,
        alignment=1,
        spaceAfter=25
    )

    cert_heading = ParagraphStyle(
        'CertHeading',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=13,
        leading=17,
        textColor=CLR_BLACK,
        alignment=1,
        spaceAfter=20
    )

    chapter_label = ParagraphStyle(
        'ChapterLabel',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=13,
        leading=17,
        textColor=CLR_BLACK,
        alignment=1,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True
    )

    chapter_title = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=13,
        leading=17,
        textColor=CLR_BLACK,
        alignment=1,
        spaceBefore=0,
        spaceAfter=14,
        keepWithNext=True
    )

    sec_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=11,
        leading=15,
        textColor=CLR_BLACK,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    subsec_heading = ParagraphStyle(
        'SubSecHeading',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=10,
        leading=14,
        textColor=CLR_BLACK,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_text = ParagraphStyle(
        'BodyTextExact',
        parent=styles['Normal'],
        fontName=f_roman,
        fontSize=10,
        leading=15,
        textColor=CLR_BLACK,
        alignment=4,  # Justified
        spaceAfter=6
    )

    bullet_text = ParagraphStyle(
        'BulletTextExact',
        parent=styles['Normal'],
        fontName=f_roman,
        fontSize=10,
        leading=14.5,
        textColor=CLR_BLACK,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_head = ParagraphStyle(
        'THeadExact',
        parent=styles['Normal'],
        fontName=f_bold,
        fontSize=9,
        leading=12,
        textColor=CLR_BLACK
    )

    table_cell = ParagraphStyle(
        'TCellExact',
        parent=styles['Normal'],
        fontName=f_roman,
        fontSize=8.5,
        leading=11.5,
        textColor=CLR_BLACK
    )

    code_font = ParagraphStyle(
        'CodeFontExact',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=CLR_BLACK
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE / COVER PAGE (Sample Page 1)
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("A PROJECT REPORT<br/>ON", cover_label))
    story.append(Spacer(1, 25))

    story.append(Paragraph("CYBERSECURITY RISK MANAGEMENT SYSTEM", cover_title_red))
    story.append(Spacer(1, 35))

    story.append(Paragraph("<i>Submitted to</i>", ParagraphStyle('SubTo', fontName=f_italic, fontSize=11, alignment=1)))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>The Department of Computer Application</b>", ParagraphStyle('Dept', fontName=f_bold, fontSize=12, alignment=1)))
    story.append(Spacer(1, 35))

    story.append(Paragraph("<i>In Partial fulfilment of the requirements for the<br/>3<sup>rd</sup> Semester Project of</i>", ParagraphStyle('InPart', fontName=f_italic, fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>MASTER OF COMPUTER APPLICATION (MCA)</b>", ParagraphStyle('MCA', fontName=f_bold, fontSize=12.5, alignment=1)))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Academic Year: 2026-2027</b>", ParagraphStyle('AY', fontName=f_bold, fontSize=10.5, alignment=1)))
    story.append(Spacer(1, 45))

    # University Logo Banner Block
    univ_cell = [
        [Paragraph("<font size='14' color='#CC0000'><b>SILVER OAK UNIVERSITY</b></font><br/><font size='8' color='#333333'>EDUCATION TO INNOVATION</font>", ParagraphStyle('UB', fontName=f_bold, alignment=1))]
    ]
    t_ub = Table(univ_cell, colWidths=[400])
    t_ub.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_ub)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Silver Oak College of Computer Application<br/>Department of Computer Application</b>", ParagraphStyle('ColD', fontName=f_bold, fontSize=11, leading=15, alignment=1)))
    story.append(Spacer(1, 60))

    # Submitted By / Guided By
    sub_guide_table = [
        [
            Paragraph("<b>Submitted By:</b>", ParagraphStyle('SB', fontName=f_bold, fontSize=10.5)),
            Paragraph("<b>Guided By:</b>", ParagraphStyle('GB', fontName=f_bold, fontSize=10.5))
        ],
        [
            Paragraph(f"{STUDENT_NAME}<br/>{ENROLLMENT_NO}", ParagraphStyle('SBN', fontName=f_roman, fontSize=10, leading=14)),
            Paragraph("Mr. / Ms. Guide Name<br/>Assistant Professor, Dept. of CA", ParagraphStyle('GBN', fontName=f_roman, fontSize=10, leading=14))
        ]
    ]
    t_sg = Table(sub_guide_table, colWidths=[250, 250])
    t_sg.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sg)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CERTIFICATE (Sample Page 2 - ii)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<font size='14' color='#CC0000'><b>SILVER OAK UNIVERSITY</b></font><br/><font size='8' color='#333333'>EDUCATION TO INNOVATION</font>", ParagraphStyle('CertUniv', fontName=f_bold, alignment=1)))
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_BORDER, spaceBefore=0, spaceAfter=25))

    story.append(Paragraph("<b>CERTIFICATE</b>", cert_heading))
    story.append(Spacer(1, 25))

    story.append(Paragraph("<b>Date:</b> ______________", ParagraphStyle('CertDate', fontName=f_bold, fontSize=10.5, alignment=2)))
    story.append(Spacer(1, 35))

    cert_text = (
        f"This is to certify that the project entitled “<font color='#CC0000'><b>CYBERSECURITY RISK MANAGEMENT SYSTEM</b></font>” "
        f"has been carried out by <font color='#CC0000'><u><b>{STUDENT_NAME} ({ENROLLMENT_NO})</b></u></font> under the guidance of "
        f"<font color='#CC0000'><u><b>Project Guide Name</b></u></font> in fulfillment of the 3rd Semester Minor Project (CAM6053C) at "
        f"Silver Oak College of Computer Application, Silver Oak University, Ahmedabad during academic year 2026-2027."
    )
    story.append(Paragraph(cert_text, ParagraphStyle('CertBodyExact', parent=body_text, fontSize=10.5, leading=18)))
    story.append(Spacer(1, 180))

    cert_sig = [
        [
            Paragraph("<b>Internal Guide</b><br/>Mr./Ms. Guide Name", ParagraphStyle('IG', fontName=f_roman, fontSize=10, leading=14)),
            Paragraph("<b>External Examiner</b><br/>&nbsp;", ParagraphStyle('EE', fontName=f_roman, fontSize=10, leading=14, alignment=2))
        ],
        [
            Spacer(1, 55),
            Spacer(1, 55)
        ],
        [
            Paragraph("<b>Head of Department</b><br/>Department of Computer Application", ParagraphStyle('HOD', fontName=f_roman, fontSize=10, leading=14, alignment=1)),
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
    # PAGE 3: STUDENT DECLARATION (Sample Page 3 - iii)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>STUDENT DECLARATION</b>", cert_heading))
    story.append(Spacer(1, 35))

    decl_p1 = (
        f"I hereby declare that the project entitled \"<font color='#CC0000'><b>CYBERSECURITY RISK MANAGEMENT SYSTEM</b></font>\" "
        f"submitted in partial fulfilment of the requirements for the 3rd Semester of Master of Computer Application (MCA) is an original "
        f"work carried out by me under the guidance of <font color='#CC0000'><u><b>Guide Name</b></u></font>."
    )
    decl_p2 = (
        "I further declare that this project report, or any part thereof, has not been submitted by me or any other person for "
        "the award of any other degree or diploma of this or any other university."
    )
    decl_p3 = (
        "I also declare that all the information furnished in this project report is based on my own study, analysis, and implementation, "
        "and due acknowledgement has been made wherever the work of others has been referred to."
    )
    story.append(Paragraph(decl_p1, ParagraphStyle('DP1', parent=body_text, fontSize=10.5, leading=17)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(decl_p2, ParagraphStyle('DP2', parent=body_text, fontSize=10.5, leading=17)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(decl_p3, ParagraphStyle('DP3', parent=body_text, fontSize=10.5, leading=17)))
    story.append(Spacer(1, 180))

    decl_sig = [
        [
            Paragraph("Place: Ahmedabad<br/>Date: ______________", ParagraphStyle('DPlace', fontName=f_roman, fontSize=10, leading=16)),
            Paragraph(f"<b>Signature of the Student</b><br/><br/>{STUDENT_NAME}<br/>Enrollment No. {ENROLLMENT_NO}", ParagraphStyle('DSig', fontName=f_roman, fontSize=10, leading=15, alignment=2))
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
    # PAGE 4: ACKNOWLEDGMENT (Sample Page 4 - iv)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ACKNOWLEDGMENT</b>", cert_heading))
    story.append(Spacer(1, 30))

    ack_p1 = (
        f"The development of the <font color='#CC0000'><u><b>Cybersecurity Risk Management System</b></u></font> was a collaborative "
        f"undertaking, and I am deeply grateful to all who contributed to its successful completion."
    )
    ack_p2 = (
        f"I extend my sincere appreciation to <font color='#CC0000'><u><b>Project_Guide_Name</b></u></font> for his/her invaluable "
        f"guidance, support, and expertise throughout this project. His/Her insightful feedback and direction were instrumental in "
        f"shaping the system's design and functionality."
    )
    ack_p3 = (
        f"I am also grateful to the Department of Computer Application, Silver Oak College of Computer Application, for providing "
        f"the essential resources and infrastructure that made the development of the "
        f"<font color='#CC0000'><u><b>Cybersecurity Risk Management System</b></u></font> possible. Their support was invaluable."
    )
    ack_p4 = (
        f"Furthermore, I would like to thank the <font color='#CC0000'><u><b>security staff</b></u></font> and <font color='#CC0000'><u><b>student members</b></u></font> "
        f"who generously participated in the requirement-gathering and testing phases. Their feedback was crucial in identifying areas "
        f"for improvement and ensuring the system effectively addresses the real-world demands of a risk governance environment."
    )
    ack_p5 = (
        "This project would not have been possible without the collective efforts of everyone involved. I am truly grateful for "
        "their contributions and unwavering support."
    )

    story.append(Paragraph(ack_p1, ParagraphStyle('AP1', parent=body_text, fontSize=10.5, leading=16.5)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(ack_p2, ParagraphStyle('AP2', parent=body_text, fontSize=10.5, leading=16.5)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(ack_p3, ParagraphStyle('AP3', parent=body_text, fontSize=10.5, leading=16.5)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(ack_p4, ParagraphStyle('AP4', parent=body_text, fontSize=10.5, leading=16.5)))
    story.append(Spacer(1, 14))
    story.append(Paragraph(ack_p5, ParagraphStyle('AP5', parent=body_text, fontSize=10.5, leading=16.5)))
    story.append(Spacer(1, 80))

    story.append(Paragraph(f"{STUDENT_NAME}<br/>Enrollment No. {ENROLLMENT_NO}", ParagraphStyle('AckSig', fontName=f_roman, fontSize=10, leading=14, alignment=2)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: ABSTRACT (Sample Page 5 - v)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>ABSTRACT</b>", cert_heading))
    story.append(Spacer(1, 28))

    abs_p1 = (
        "The Cybersecurity Risk Management System is a computerized application developed to automate cybersecurity risk assessment "
        "operations and replace traditional manual record-keeping with an efficient and user-friendly solution. The system manages "
        "asset cataloguing, threat registration, qualitative risk scoring, fine-grained mitigation tracking, and report generation "
        "using a centralized database."
    )
    abs_p2 = (
        "Developed using a modular approach, the system includes separate modules for asset management, risk assessment, calculation, "
        "and transaction auditing. It provides role-based access for administrators and security staff, ensuring secure management of "
        "cybersecurity records. Advanced search and filtering features enable users to quickly locate risks by title, asset, category, or level."
    )
    abs_p3 = (
        "The primary objective of the project is to reduce manual effort, minimize human errors, and provide accurate and timely access "
        "to institutional risk posture. The system also generates reports such as overdue mitigations, high-severity risks, and audit collection "
        "summaries to support effective cybersecurity administration. The project follows the Software Development Life Cycle (SDLC), "
        "including requirement analysis, system design, implementation, testing, and deployment."
    )
    abs_p4 = (
        "The developed system improves the efficiency, accuracy, and reliability of risk governance operations while enhancing the overall "
        "user experience. It also provides a scalable foundation for future enhancements."
    )

    story.append(Paragraph(abs_p1, ParagraphStyle('AbP1', parent=body_text, fontSize=10, leading=15.5)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(abs_p2, ParagraphStyle('AbP2', parent=body_text, fontSize=10, leading=15.5)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(abs_p3, ParagraphStyle('AbP3', parent=body_text, fontSize=10, leading=15.5)))
    story.append(Spacer(1, 10))
    story.append(Paragraph(abs_p4, ParagraphStyle('AbP4', parent=body_text, fontSize=10, leading=15.5)))
    story.append(Spacer(1, 16))

    story.append(Paragraph("<i>Keywords:</i> Cybersecurity Risk Management System, Automation, Database Management System (DBMS), SDLC, Web Application.", ParagraphStyle('KW', fontName=f_italic, fontSize=9.5, leading=14)))
    story.append(Spacer(1, 35))

    story.append(Paragraph("<font color='#CC0000'><i>(Abstract will be different for each students as per their title selected)</i></font>", ParagraphStyle('AbsNote', fontName=f_italic, fontSize=9.5, leading=14)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: TABLE OF CONTENTS (Part 1 - vi) (Sample Page 6)
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>TABLE OF CONTENTS</b>", cert_heading))
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
        p_title = Paragraph(title_txt, ParagraphStyle('TOCItem', fontName=f_roman, fontSize=9.5, leading=13))
        p_page = Paragraph(pg, ParagraphStyle('TOCPg', fontName=f_roman, fontSize=9.5, leading=13, alignment=2))
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
    # PAGE 7: TABLE OF CONTENTS (Part 2 - vii) (Sample Page 7)
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
        p_title = Paragraph(title_txt, ParagraphStyle('TOCItem2', fontName=f_roman, fontSize=9.5, leading=14))
        p_page = Paragraph(pg, ParagraphStyle('TOCPg2', fontName=f_roman, fontSize=9.5, leading=14, alignment=2))
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
    # PAGE 8: LIST OF FIGURES (viii) (Sample Page 8)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF FIGURES</b>", cert_heading))
    story.append(Spacer(1, 25))

    lof_data = [
        [Paragraph("<b>Figure No.</b>", table_head), Paragraph("<b>Title</b>", table_head), Paragraph("<b>Page No.</b>", table_head)],
        [Paragraph("Figure 3.1", table_cell), Paragraph("Use Case Diagram of Cybersecurity Risk Management System", table_cell), Paragraph("5", table_cell)],
        [Paragraph("Figure 4.1", table_cell), Paragraph("System Architecture Diagram", table_cell), Paragraph("6", table_cell)],
        [Paragraph("Figure 4.2", table_cell), Paragraph("Data Flow Diagram (Level 0)", table_cell), Paragraph("6", table_cell)],
        [Paragraph("Figure 4.3", table_cell), Paragraph("Data Flow Diagram (Level 1)", table_cell), Paragraph("6", table_cell)],
        [Paragraph("Figure 4.4", table_cell), Paragraph("Entity-Relationship Diagram", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Figure 4.5", table_cell), Paragraph("Class Diagram", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Figure 4.6", table_cell), Paragraph("Sequence Diagram — Risk Evaluation Process", table_cell), Paragraph("7", table_cell)],
        [Paragraph("Figure 5.1", table_cell), Paragraph("Login Module Screenshot", table_cell), Paragraph("9", table_cell)],
        [Paragraph("Figure 5.2", table_cell), Paragraph("Executive Dashboard & Risk Heatmap Screenshot", table_cell), Paragraph("9", table_cell)],
        [Paragraph("Figure 6.1", table_cell), Paragraph("Graph Showing Test Case Pass/Fail Ratio", table_cell), Paragraph("11", table_cell)],
    ]
    t_lof = Table(lof_data, colWidths=[80, 340, 80])
    t_lof.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_lof)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: LIST OF TABLES (ix) (Sample Page 9)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF TABLES</b>", cert_heading))
    story.append(Spacer(1, 25))

    lot_data = [
        [Paragraph("<b>Table No.</b>", table_head), Paragraph("<b>Title</b>", table_head), Paragraph("<b>Page No.</b>", table_head)],
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
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_lot)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: LIST OF ABBREVIATIONS (x) (Sample Page 10)
    # =========================================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>LIST OF ABBREVIATIONS</b>", cert_heading))
    story.append(Spacer(1, 25))

    loa_data = [
        [Paragraph("<b>Abbreviation</b>", table_head), Paragraph("<b>Full Form</b>", table_head)],
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
        [Paragraph("ACID", table_cell), Paragraph("Atomicity, Consistency, Isolation, Durability (Database Transaction Guarantees)", table_cell)],
        [Paragraph("RBAC", table_cell), Paragraph("Role-Based Access Control (Admin vs. Analyst Privileges)", table_cell)],
        [Paragraph("PBKDF2", table_cell), Paragraph("Password-Based Key Derivation Function 2 (Key Stretching Cryptographic Algorithm)", table_cell)],
        [Paragraph("HMAC", table_cell), Paragraph("Hash-based Message Authentication Code (Cryptographic Message Authentication)", table_cell)],
        [Paragraph("SHA", table_cell), Paragraph("Secure Hash Algorithm (256-bit One-Way Cryptographic Digest)", table_cell)],
    ]
    t_loa = Table(loa_data, colWidths=[110, 390])
    t_loa.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_loa)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11 (Body Page 1): CHAPTER 1 — Introduction (Sample Page 11)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 1</b>", chapter_label))
    story.append(Paragraph("<b>Introduction</b>", chapter_title))

    story.append(Paragraph("<b>1.1 Background</b>", sec_heading))
    intro_bg = (
        "Organizations have traditionally served as custodians of critical IT infrastructure, providing access to digital services, "
        "databases, and operational networks to staff, faculty, and stakeholders. However, the manual processes historically used to manage "
        "cybersecurity risk operations — such as maintaining paper registers and desktop spreadsheets for asset records, evaluating "
        "threat scenarios, and calculating risk levels — are time-consuming, prone to human error, and difficult to scale as the volume of "
        "assets and threats grows.<br/><br/>"
        "With the rapid advancement of information technology, it has become both feasible and necessary to computerize such repetitive "
        "and record-intensive tasks. A Cybersecurity Risk Management System automates the core functions of risk governance, including "
        "asset cataloguing, qualitative risk calculation, treatment tracking, and report generation, thereby improving efficiency, accuracy, "
        "and accessibility of information for both security analysts and administrators."
    )
    story.append(Paragraph(intro_bg, body_text))

    story.append(Paragraph("<b>1.2 Problem Statement</b>", sec_heading))
    intro_ps = (
        "The existing manual risk tracking system at many institutions relies on physical registers and spreadsheets to track IT assets "
        "and operational threats. This approach suffers from several drawbacks: difficulty in searching for a specific risk scenario, "
        "delays in checking asset ownership and status, inaccurate fine calculation and subjective scoring, lack of real-time reporting, "
        "and the risk of losing records due to file corruption. There is, therefore, a need for a centralized, computerized system that "
        "can manage all risk management operations efficiently, accurately, and securely."
    )
    story.append(Paragraph(intro_ps, body_text))

    story.append(Paragraph("<b>1.3 Objectives of the Project</b>", sec_heading))
    story.append(Paragraph("• To design and develop a centralized database for storing asset and risk information.", bullet_text))
    story.append(Paragraph("• To automate the process of risk evaluation, score calculation, and treatment tracking.", bullet_text))
    story.append(Paragraph("• To provide an efficient search mechanism for locating risks by title, asset, category, or level.", bullet_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12 (Body Page 2): CHAPTER 1 (Cont.) (Sample Page 12)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("• To generate reports such as overdue mitigations, high-severity risks, and audit collection summaries.", bullet_text))
    story.append(Paragraph("• To provide role-based access control for administrators and security staff.", bullet_text))
    story.append(Paragraph("• To reduce manual effort, paperwork, and human error in risk management operations.", bullet_text))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.4 Scope of the Project</b>", sec_heading))
    intro_scope = (
        "The scope of this project is limited to automating the core functional areas of an institutional or departmental risk register, "
        "namely asset cataloguing, risk scenario evaluation, treatment lifecycle tracking, fine audit logging, and basic reporting. "
        "The system is designed for use by risk administrators and staff; it does not, in its current version, include external cloud "
        "synchronization or integration with third-party automated vulnerability scanners, both of which are identified as areas for "
        "future enhancement."
    )
    story.append(Paragraph(intro_scope, body_text))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>1.5 Organization of the Report</b>", sec_heading))
    intro_org = (
        "This report is organized into seven chapters. Chapter 1 introduces the project background, problem statement, objectives, "
        "and scope. Chapter 2 reviews existing risk management solutions and related literature. Chapter 3 details the system requirement "
        "analysis, including functional and non-functional requirements. Chapter 4 describes the system design and methodology, including "
        "architecture, data flow, and database design. Chapter 5 discusses the implementation details and coding approach. Chapter 6 presents "
        "the testing strategy, test cases, and results analysis. Finally, Chapter 7 concludes the report and outlines directions for future work."
    )
    story.append(Paragraph(intro_org, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13 (Body Page 3): CHAPTER 2 — Literature Review (Sample Page 13)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 2</b>", chapter_label))
    story.append(Paragraph("<b>Literature Review</b>", chapter_title))

    story.append(Paragraph("<b>2.1 Existing Systems</b>", sec_heading))
    lit_ex = (
        "Several commercial and open-source risk management solutions are currently available, ranging from simple spreadsheet-based "
        "tracking tools to comprehensive enterprise systems such as ServiceNow GRC and RSA Archer. These systems typically provide "
        "cataloguing, circulation, and reporting modules; however, many are either too expensive for small institutional departments or "
        "too generic to be tailored to the specific workflow of a college-level risk register.<br/><br/>"
        "A review of academic literature on cybersecurity automation indicates that computerized systems significantly reduce the average "
        "time required for threat evaluation and review transactions, improve the accuracy of risk calculation, and provide better visibility "
        "into security posture through real-time reporting, when compared with manual record-keeping systems."
    )
    story.append(Paragraph(lit_ex, body_text))

    story.append(Paragraph("<b>2.2 Comparative Analysis</b>", sec_heading))
    lit_comp = (
        "A comparative study of existing systems reveals common strengths such as centralized cataloguing, automated risk calculation, "
        "and multi-user access. Common limitations include high licensing costs, complex deployment requirements, and limited customization "
        "options for smaller institutions. The proposed Cybersecurity Risk Management System aims to combine the essential features of these "
        "existing solutions into a lightweight, cost-effective, and customizable application suited to a college-level department."
    )
    story.append(Paragraph(lit_comp, body_text))

    story.append(Paragraph("<b>2.3 Summary</b>", sec_heading))
    lit_sum = (
        "The literature review establishes a strong case for automating risk management operations and highlights the specific gaps — namely "
        "cost, complexity, and lack of customization — that the proposed system seeks to address through a modular, database-driven design."
    )
    story.append(Paragraph(lit_sum, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 14 (Body Page 4): CHAPTER 3 — Requirements (Sample Page 14)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 3</b>", chapter_label))
    story.append(Paragraph("<b>System Requirement Analysis</b>", chapter_title))

    story.append(Paragraph("<b>3.1 Functional Requirements</b>", sec_heading))
    story.append(Paragraph("Functional requirements define the specific behaviours and functions that the system must support. Table 3.1 summarizes the key functional requirements identified for the Cybersecurity Risk Management System.", body_text))

    fr_data = [
        [Paragraph("<b>Req. ID</b>", table_head), Paragraph("<b>Requirement Description</b>", table_head)],
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
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_fr)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>3.2 Non-Functional Requirements</b>", sec_heading))
    story.append(Paragraph("• <b>Usability:</b> The system shall provide a simple and intuitive graphical user interface.", bullet_text))
    story.append(Paragraph("• <b>Reliability:</b> The system shall ensure accurate and consistent data storage and retrieval via ACID transactional consistency.", bullet_text))
    story.append(Paragraph("• <b>Performance:</b> Search and transaction operations shall complete within two seconds under normal load.", bullet_text))
    story.append(Paragraph("• <b>Security:</b> The system shall restrict access to authorized users through login credentials and PBKDF2-HMAC-SHA256 password hashing.", bullet_text))
    story.append(Paragraph("• <b>Maintainability:</b> The modular design shall allow easy addition of new features in the future.", bullet_text))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>3.3 Hardware Requirements</b>", sec_heading))
    hw_data = [
        [Paragraph("<b>Component</b>", table_head), Paragraph("<b>Specification</b>", table_head)],
        [Paragraph("Processor", table_cell), Paragraph("Intel Core i3 or above", table_cell)],
        [Paragraph("RAM", table_cell), Paragraph("4 GB or above", table_cell)],
        [Paragraph("Hard Disk", table_cell), Paragraph("250 GB or above", table_cell)],
        [Paragraph("Monitor", table_cell), Paragraph("Standard colour monitor", table_cell)],
    ]
    t_hw = Table(hw_data, colWidths=[150, 350])
    t_hw.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_hw)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 15 (Body Page 5): CHAPTER 3 (Cont.) (Sample Page 15)
    # =========================================================================
    story.append(Paragraph("<b>3.4 Software Requirements</b>", sec_heading))
    sw_data = [
        [Paragraph("<b>Component</b>", table_head), Paragraph("<b>Specification</b>", table_head)],
        [Paragraph("Operating System", table_cell), Paragraph("Windows 10 / 11", table_cell)],
        [Paragraph("Front-End", table_cell), Paragraph("HTML, CSS, JavaScript", table_cell)],
        [Paragraph("Back-End", table_cell), Paragraph("Python (Standard Library: http.server, sqlite3)", table_cell)],
        [Paragraph("Database", table_cell), Paragraph("SQLite", table_cell)],
        [Paragraph("IDE", table_cell), Paragraph("Visual Studio Code", table_cell)],
    ]
    t_sw = Table(sw_data, colWidths=[150, 350])
    t_sw.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_sw)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>3.5 Feasibility Study</b>", sec_heading))
    story.append(Paragraph("<b>3.5.1 Technical Feasibility</b>", subsec_heading))
    story.append(Paragraph(
        "The technologies required for developing the proposed system — including the chosen programming language, "
        "database management system, and development tools — are freely available, well-documented, and within the technical "
        "capability of the development team.", body_text
    ))

    story.append(Paragraph("<b>3.5.2 Economic Feasibility</b>", subsec_heading))
    story.append(Paragraph(
        "The project relies primarily on open-source and freely available tools, resulting in negligible development cost. "
        "The long-term benefits, in terms of reduced manual labour and improved accuracy, significantly outweigh the minimal implementation cost.", body_text
    ))

    story.append(Paragraph("<b>3.5.3 Operational Feasibility</b>", subsec_heading))
    story.append(Paragraph(
        "The proposed system is designed with a simple and intuitive interface, requiring minimal training for staff to operate "
        "effectively, thereby ensuring high operational feasibility.", body_text
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("[Figure 3.1: Use Case Diagram of Cybersecurity Risk Management System — to be inserted here]", ParagraphStyle('FN', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 16 (Body Page 6): CHAPTER 4 — System Design (Sample Page 16)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 4</b>", chapter_label))
    story.append(Paragraph("<b>System Design and Methodology</b>", chapter_title))

    story.append(Paragraph("<b>4.1 System Architecture</b>", sec_heading))
    story.append(Paragraph(
        "The Cybersecurity Risk Management System follows a three-tier architecture consisting of a presentation layer "
        "(user interface), an application layer (business logic), and a data layer (database). This separation of concerns "
        "improves maintainability and allows each layer to be modified independently without affecting the others.", body_text
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("[Figure 4.1: System Architecture Diagram — to be inserted here]", ParagraphStyle('F41', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.2 Data Flow Diagrams</b>", sec_heading))
    story.append(Paragraph(
        "The Data Flow Diagram (DFD) illustrates the flow of information through the system. The Level 0 DFD (context diagram) "
        "represents the system as a single process interacting with external entities such as Admin and Staff. The Level 1 DFD "
        "decomposes this into major sub-processes, including Asset Management, Risk Evaluation, and Report Generation.", body_text
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("[Figure 4.2: Data Flow Diagram (Level 0) — to be inserted here]", ParagraphStyle('F42', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))
    story.append(Paragraph("[Figure 4.3: Data Flow Diagram (Level 1) — to be inserted here]", ParagraphStyle('F43', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.3 Entity-Relationship Diagram</b>", sec_heading))
    story.append(Paragraph(
        "The Entity-Relationship (ER) Diagram models the relationships among the key entities of the system, namely Asset, "
        "Risk, and AuditLog. Each Asset can be involved in multiple Risks, and each Risk references its parent Asset, establishing "
        "a one-to-many relationship resolved through foreign keys.", body_text
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("[Figure 4.4: Entity-Relationship Diagram — to be inserted here]", ParagraphStyle('F44', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>4.4 Database Design</b>", sec_heading))
    story.append(Paragraph("The database for the Cybersecurity Risk Management System consists of the following major tables, described below.", body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 17 (Body Page 7): CHAPTER 4 (Cont.) (Sample Page 17)
    # =========================================================================
    story.append(Paragraph("<i>4.4.1 tbl_Asset</i>", ParagraphStyle('SubItal1', fontName=f_bold, fontSize=10, textColor=colors.HexColor('#003366'), spaceBefore=2, spaceAfter=4)))
    ast_cols = [
        [Paragraph("<b>Field Name</b>", table_head), Paragraph("<b>Data Type</b>", table_head), Paragraph("<b>Description</b>", table_head)],
        [Paragraph("AssetID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique identifier for each asset", table_cell)],
        [Paragraph("Name", table_cell), Paragraph("Varchar(150)", table_cell), Paragraph("Title of the asset", table_cell)],
        [Paragraph("Type", table_cell), Paragraph("Varchar(50)", table_cell), Paragraph("Classification (Data, System, Device, Service)", table_cell)],
        [Paragraph("Owner", table_cell), Paragraph("Varchar(100)", table_cell), Paragraph("Responsible asset owner / custodian", table_cell)],
    ]
    t_ast = Table(ast_cols, colWidths=[120, 100, 280])
    t_ast.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_ast)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<i>4.4.2 tbl_Risk</i>", ParagraphStyle('SubItal2', fontName=f_bold, fontSize=10, textColor=colors.HexColor('#003366'), spaceBefore=2, spaceAfter=4)))
    rsk_cols = [
        [Paragraph("<b>Field Name</b>", table_head), Paragraph("<b>Data Type</b>", table_head), Paragraph("<b>Description</b>", table_head)],
        [Paragraph("RiskID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique identifier for each risk", table_cell)],
        [Paragraph("Title", table_cell), Paragraph("Varchar(200)", table_cell), Paragraph("Threat scenario title", table_cell)],
        [Paragraph("AssetID", table_cell), Paragraph("Int (FK)", table_cell), Paragraph("Reference to tbl_Asset", table_cell)],
        [Paragraph("Likelihood", table_cell), Paragraph("Int", table_cell), Paragraph("Likelihood rating (1-3)", table_cell)],
        [Paragraph("Impact", table_cell), Paragraph("Int", table_cell), Paragraph("Impact rating (1-3)", table_cell)],
        [Paragraph("Score", table_cell), Paragraph("Int", table_cell), Paragraph("Calculated score (Likelihood x Impact)", table_cell)],
        [Paragraph("Status", table_cell), Paragraph("Varchar(30)", table_cell), Paragraph("Remediation stage (Open, Treated, Closed)", table_cell)],
    ]
    t_rsk = Table(rsk_cols, colWidths=[120, 100, 280])
    t_rsk.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rsk)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<i>4.4.3 tbl_AuditLog</i>", ParagraphStyle('SubItal3', fontName=f_bold, fontSize=10, textColor=colors.HexColor('#003366'), spaceBefore=2, spaceAfter=4)))
    aud_cols = [
        [Paragraph("<b>Field Name</b>", table_head), Paragraph("<b>Data Type</b>", table_head), Paragraph("<b>Description</b>", table_head)],
        [Paragraph("LogID", table_cell), Paragraph("Int (PK)", table_cell), Paragraph("Unique identifier for each transaction", table_cell)],
        [Paragraph("Action", table_cell), Paragraph("Varchar(50)", table_cell), Paragraph("Action performed (CREATE, UPDATE, DELETE)", table_cell)],
        [Paragraph("UserID", table_cell), Paragraph("Int", table_cell), Paragraph("Reference to authorized user", table_cell)],
        [Paragraph("Timestamp", table_cell), Paragraph("Datetime", table_cell), Paragraph("Timestamp of record modification", table_cell)],
    ]
    t_aud = Table(aud_cols, colWidths=[120, 100, 280])
    t_aud.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_aud)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>4.5 UML Diagrams</b>", sec_heading))
    story.append(Paragraph(
        "Unified Modeling Language (UML) diagrams were used to model the system from different perspectives. "
        "The Use Case Diagram represents the interactions between actors (Admin, Staff) and the system. The Class Diagram "
        "represents the static structure of the system in terms of classes, attributes, and methods. The Sequence Diagram "
        "illustrates the interaction sequence for the risk evaluation process.", body_text
    ))
    story.append(Spacer(1, 2))
    story.append(Paragraph("[Figure 3.1: Use Case Diagram — to be inserted here]", ParagraphStyle('U1', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))
    story.append(Paragraph("[Figure 4.5: Class Diagram — to be inserted here]", ParagraphStyle('U2', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))
    story.append(Paragraph("[Figure 4.6: Sequence Diagram — Risk Assessment Process — to be inserted here]", ParagraphStyle('U3', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 18 (Body Page 8): CHAPTER 5 — Implementation (Sample Page 18)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 5</b>", chapter_label))
    story.append(Paragraph("<b>Implementation and Coding</b>", chapter_title))

    story.append(Paragraph("<b>5.1 Development Environment</b>", sec_heading))
    story.append(Paragraph(
        "The Cybersecurity Risk Management System was developed using a standard integrated development environment configured "
        "with the front-end, back-end, and database technologies listed in Section 3.4. Version control was maintained throughout "
        "development to track changes and manage revisions of the source code.", body_text
    ))

    story.append(Paragraph("<b>5.2 Module Description</b>", sec_heading))
    story.append(Paragraph("<b>5.2.1 Login Module</b>", subsec_heading))
    story.append(Paragraph("This module authenticates Admin and Staff users based on a username and password, and redirects them to the appropriate dashboard based on their assigned role.", body_text))

    story.append(Paragraph("<b>5.2.2 Asset Management Module</b>", subsec_heading))
    story.append(Paragraph("This module allows authorized users to add, update, delete, and search asset records stored in the database, including details such as name, category, and owner.", body_text))

    story.append(Paragraph("<b>5.2.3 Risk Assessment Module</b>", subsec_heading))
    story.append(Paragraph("This module handles the registration, updating, and evaluation of risk scenarios, along with viewing a risk's active status and historical treatment records.", body_text))

    story.append(Paragraph("<b>5.2.4 Calculation Module</b>", subsec_heading))
    story.append(Paragraph("This module manages the calculation of risk scores, automatically evaluates Likelihood and Impact ratings, and computes applicable qualitative risk categories based on configurable matrix rules.", body_text))

    story.append(Paragraph("<b>5.2.5 Report Module</b>", subsec_heading))
    story.append(Paragraph("This module generates reports such as currently open risks, high-severity risks, and audit collection summaries, which can be viewed or exported by the administrator.", body_text))

    story.append(Paragraph("<b>5.3 Coding Standards</b>", sec_heading))
    story.append(Paragraph(
        "Consistent naming conventions, indentation, and inline comments were followed throughout the codebase to improve "
        "readability and maintainability. Reusable functions were used wherever possible to minimize code duplication, and input "
        "validation was implemented at both the client and server sides to maintain data integrity.", body_text
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 19 (Body Page 9): CHAPTER 5 (Cont.) (Sample Page 19)
    # =========================================================================
    story.append(Paragraph("wherever possible to minimize code duplication, and input validation was implemented at both the client and server sides to maintain data integrity.", body_text))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>5.4 Sample Code Snippets</b>", sec_heading))
    story.append(Paragraph(
        "The following illustrative snippet demonstrates the risk calculation logic used in the Calculation Module (sample pseudocode for reference purposes):", body_text
    ))
    story.append(Spacer(1, 4))

    code_box_content = (
        "IF Likelihood &gt;= 1 AND Impact &gt;= 1 THEN Score = Likelihood * Impact "
        "IF Score &gt;= 6 THEN Level = 'High' ELSE IF Score &gt;= 3 THEN Level = 'Medium' "
        "ELSE Level = 'Low' END IF ELSE Level = 'Undefined' END IF"
    )
    t_code = Table([[Paragraph(code_box_content, code_font)]], colWidths=[500])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CLR_BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 14))

    img_login = os.path.join(media_dir, "screen_login.png")
    if os.path.exists(img_login):
        story.append(Paragraph("<b>Figure 5.1: Login Module Screenshot</b>", subsec_heading))
        story.append(Spacer(1, 2))
        story.append(Image(img_login, width=320, height=130))
        story.append(Spacer(1, 8))

    img_dash = os.path.join(media_dir, "screen_dashboard.png")
    if os.path.exists(img_dash):
        story.append(Paragraph("<b>Figure 5.2: Executive Dashboard & Risk Heatmap Screenshot</b>", subsec_heading))
        story.append(Spacer(1, 2))
        story.append(Image(img_dash, width=440, height=160))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 20 (Body Page 10): CHAPTER 6 — Testing (Sample Page 20)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 6</b>", chapter_label))
    story.append(Paragraph("<b>Testing and Results Analysis</b>", chapter_title))

    story.append(Paragraph("<b>6.1 Testing Objectives</b>", sec_heading))
    story.append(Paragraph(
        "The primary objective of testing was to verify that each module of the Cybersecurity Risk Management System functions "
        "correctly, individually and in integration with other modules, and that the system meets the functional and non-functional "
        "requirements identified in Chapter 3.", body_text
    ))

    story.append(Paragraph("<b>6.2 Testing Methods</b>", sec_heading))
    story.append(Paragraph(
        "A combination of Unit Testing, Integration Testing, and User Acceptance Testing (UAT) was performed. Unit testing verified "
        "individual functions such as risk calculation and search filtering. Integration testing verified the correct interaction "
        "between the Asset, Risk, and AuditLog modules. User acceptance testing was conducted with sample institutional staff to validate "
        "real-world usability.", body_text
    ))

    story.append(Paragraph("<b>6.3 Test Cases</b>", sec_heading))
    story.append(Paragraph("<b>6.3.1 Login Module</b>", subsec_heading))

    tc_login = [
        [Paragraph("<b>Test Case ID</b>", table_head), Paragraph("<b>Description</b>", table_head), Paragraph("<b>Expected Result</b>", table_head), Paragraph("<b>Status</b>", table_head)],
        [Paragraph("TC-01", table_cell), Paragraph("Login with valid credentials", table_cell), Paragraph("User redirected to dashboard", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-02", table_cell), Paragraph("Login with invalid password", table_cell), Paragraph("Error message displayed", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc1 = Table(tc_login, colWidths=[70, 150, 220, 60])
    t_tc1.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>6.3.2 Asset Inventory Module</b>", subsec_heading))
    tc_asset = [
        [Paragraph("<b>Test Case ID</b>", table_head), Paragraph("<b>Description</b>", table_head), Paragraph("<b>Expected Result</b>", table_head), Paragraph("<b>Status</b>", table_head)],
        [Paragraph("TC-04", table_cell), Paragraph("Add valid IT asset record", table_cell), Paragraph("Asset created and code generated", table_cell), Paragraph("Pass", table_cell)],
        [Paragraph("TC-05", table_cell), Paragraph("Add asset with missing name", table_cell), Paragraph("Error message: name required", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc2 = Table(tc_asset, colWidths=[70, 150, 220, 60])
    t_tc2.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc2)
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>6.3.3 Risk Calculation Module</b>", subsec_heading))
    tc_calc = [
        [Paragraph("<b>Test Case ID</b>", table_head), Paragraph("<b>Description</b>", table_head), Paragraph("<b>Expected Result</b>", table_head), Paragraph("<b>Status</b>", table_head)],
        [Paragraph("TC-07", table_cell), Paragraph("Calculate Low Risk (1 x 2)", table_cell), Paragraph("Score 2, Category Low assigned", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc3 = Table(tc_calc, colWidths=[70, 150, 220, 60])
    t_tc3.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc3)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 21 (Body Page 11): CHAPTER 6 (Cont.) (Sample Page 21)
    # =========================================================================
    story.append(Spacer(1, 10))
    tc_calc_cont = [
        [Paragraph("<b>Test Case ID</b>", table_head), Paragraph("<b>Description</b>", table_head), Paragraph("<b>Expected Result</b>", table_head), Paragraph("<b>Status</b>", table_head)],
        [Paragraph("TC-08", table_cell), Paragraph("Calculate High Risk (3 x 3)", table_cell), Paragraph("Score 9, Category High assigned", table_cell), Paragraph("Pass", table_cell)],
    ]
    t_tc_cont = Table(tc_calc_cont, colWidths=[70, 150, 220, 60])
    t_tc_cont.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_tc_cont)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>6.4 Results Analysis</b>", sec_heading))
    results_text = (
        "All executed test cases across the Login, Asset Inventory, and Risk Calculation modules produced the expected results, "
        "indicating that the core functionality of the Cybersecurity Risk Management System operates correctly and reliably. "
        "Minor issues identified during initial testing, such as edge-case fine calculation and status mapping, were resolved prior "
        "to final deployment. Overall, the results confirm that the system meets the functional requirements defined in Chapter 3."
    )
    story.append(Paragraph(results_text, body_text))
    story.append(Spacer(1, 10))

    story.append(Paragraph("[Figure 6.1: Graph Showing Test Case Pass/Fail Ratio — to be inserted here]", ParagraphStyle('F61', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 22 (Body Page 12): CHAPTER 7 — Conclusion (Sample Page 22)
    # =========================================================================
    story.append(Paragraph("<b>CHAPTER 7</b>", chapter_label))
    story.append(Paragraph("<b>Conclusion and Future Scope</b>", chapter_title))

    story.append(Paragraph("<b>7.1 Conclusion</b>", sec_heading))
    conc_text = (
        "The Cybersecurity Risk Management System successfully automates the core operations of a college or departmental risk register, "
        "including asset cataloguing, risk assessment, evaluation transactions, and score calculation. The system significantly reduces "
        "the manual effort involved in maintaining risk records, minimizes human error, and provides quick and accurate access to information "
        "for both risk staff and administrators. Testing confirmed that the system meets its defined functional and non-functional requirements, "
        "demonstrating the practical benefits of automation over traditional manual record-keeping."
    )
    story.append(Paragraph(conc_text, body_text))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>7.2 Future Scope</b>", sec_heading))
    story.append(Paragraph("• Integration of an Online Public Access Catalogue (OPAC) to allow department members to search the risk catalogue remotely.", bullet_text))
    story.append(Paragraph("• Implementation of a barcode/RFID-based system for faster hardware asset issue and return.", bullet_text))
    story.append(Paragraph("• Integration of an online payment gateway for compliance fee and fine payment.", bullet_text))
    story.append(Paragraph("• Development of a mobile application for members to check review dates and renew assessments.", bullet_text))
    story.append(Paragraph("• Addition of an email/SMS notification module to remind members of upcoming review dates.", bullet_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 23 (Body Page 13): BIBLIOGRAPHY & REFERENCES (Sample Page 23)
    # =========================================================================
    story.append(Paragraph("<b>BIBLIOGRAPHY & REFERENCES</b>", cert_heading))
    story.append(Spacer(1, 15))

    bib_items = [
        "[1] Author Name, \"Title of Referenced Book,\" Publisher, Edition, Year.",
        "[2] Author Name, \"Title of Referenced Research Paper,\" Journal/Conference Name, Volume, Issue, Year, Page Numbers.",
        "[3] Official documentation of the programming language / framework used (e.g., Python Reference Manual, https://docs.python.org/3/).",
        "[4] Official documentation of the development tools used (e.g., Visual Studio Code Documentation).",
        "[5] Relevant online tutorials, technical articles, or W3Schools references consulted during development.",
    ]
    for item in bib_items:
        story.append(Paragraph(item, ParagraphStyle('BibItem', parent=body_text, leftIndent=20, firstLineIndent=-20, spaceAfter=8)))

    story.append(Spacer(1, 15))
    story.append(Paragraph(
        "<font color='#CC0000'><i>Note to student: Replace the above placeholder entries with the actual books, research papers, and websites referred to during your project, formatted consistently in IEEE or APA style as instructed by your guide.</i></font>",
        ParagraphStyle('BibNoteExact', parent=body_text, fontSize=9.5, leading=14)
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 24 (Body Page 14): APPENDICES — Appendix A (Sample Page 24)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>APPENDICES</b>", cert_heading))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Appendix A Review 1 — Scanned Copy</b>", ParagraphStyle('AppAExact', fontName=f_bold, fontSize=11, alignment=1, spaceAfter=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("[Insert scanned copy of the signed Review 1 evaluation sheet here.]", ParagraphStyle('ANote', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 25 (Body Page 15): Appendix B (Sample Page 25)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Appendix B Review 2 — Scanned Copy</b>", ParagraphStyle('AppBExact', fontName=f_bold, fontSize=11, alignment=1, spaceAfter=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("[Insert scanned copy of the signed Review 2 evaluation sheet here.]", ParagraphStyle('BNote', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 26 (Body Page 16): Appendix C (Sample Page 26)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Appendix C Review 3 — Scanned Copy</b>", ParagraphStyle('AppCExact', fontName=f_bold, fontSize=11, alignment=1, spaceAfter=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("[Insert scanned copy of the signed Review 3 evaluation sheet here.]", ParagraphStyle('CNote', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 27 (Body Page 17): Appendix D (Sample Page 27)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Appendix D Review 4 — Scanned Copy</b>", ParagraphStyle('AppDExact', fontName=f_bold, fontSize=11, alignment=1, spaceAfter=15)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("[Insert scanned copy of the signed Review 4 evaluation sheet here.]", ParagraphStyle('DNote', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 28 (Body Page 18): PUBLICATION (Sample Page 28)
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>PUBLICATION / PATENT / RESEARCH OUTPUT</b>", cert_heading))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "(This section is optional and applicable only if the student has published a research paper, filed a patent, or produced any other research output based on this project.)",
        ParagraphStyle('PubNoteExact', parent=body_text, alignment=1, fontSize=10, leading=14.5)
    ))
    story.append(Spacer(1, 20))
    story.append(Paragraph("[Insert scanned copy of the publication certificate / acceptance letter / patent filing receipt here.]", ParagraphStyle('PNote', parent=body_text, alignment=1, textColor=CLR_GRAY_TEXT)))

    # Build PDF
    doc.build(story, canvasmaker=SampleExactCanvas)
    print(f"Project Report PDF generated matching sample template at: {output_pdf}")


if __name__ == "__main__":
    build_academic_pdf()
