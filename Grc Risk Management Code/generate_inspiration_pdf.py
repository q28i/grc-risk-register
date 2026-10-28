"""
Inspiration & Architectural Benchmark Reference Generator
File: GRC_Risk_Register_Architecture_Inspiration.pdf
Student: Tanvi Mishra (Enrollment No: 2504070300016)
Silver Oak College of Computer Application, Ahmedabad
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

PAGE_W, PAGE_H = letter

CLR_PRIMARY = colors.HexColor('#990000')      # Academic Crimson
CLR_HEADER_LINE = colors.HexColor('#333333')
CLR_TEXT_PRI = colors.HexColor('#111111')
CLR_BG_LIGHT = colors.HexColor('#F8F9FA')
CLR_BORDER = colors.HexColor('#D0D0D0')
CLR_BORDER_DARK = colors.HexColor('#444444')
CLR_CODE_BG = colors.HexColor('#F1F3F5')

STUDENT_NAME = "Tanvi Mishra"
ENROLLMENT_NO = "2504070300016"


class NumberedCanvas(canvas.Canvas):
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
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, total_pages):
        page_num = self._pageNumber
        self.saveState()

        # Running Header
        self.setFont("Times-Bold", 9)
        self.setFillColor(CLR_TEXT_PRI)
        self.drawString(54, PAGE_H - 36, "GRC Risk Register — Technical Inspiration & Architectural Benchmarks")
        self.setStrokeColor(CLR_HEADER_LINE)
        self.setLineWidth(0.8)
        self.line(54, PAGE_H - 42, PAGE_W - 54, PAGE_H - 42)

        # Running Footer
        self.line(54, 48, PAGE_W - 54, 48)
        self.setFont("Times-Roman", 9)
        self.drawString(54, 34, f"{STUDENT_NAME} ({ENROLLMENT_NO}) — Silver Oak College of Computer Application")
        self.drawRightString(PAGE_W - 54, 34, f"Page {page_num} of {total_pages}")

        self.restoreState()


def build_inspiration_pdf():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_pdf = os.path.join(root_dir, "GRC_Risk_Register_Architecture_Inspiration.pdf")

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

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=16,
        leading=20,
        textColor=CLR_PRIMARY,
        alignment=1,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=11,
        leading=15,
        textColor=CLR_HEADER_LINE,
        alignment=1,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=12,
        leading=16,
        textColor=CLR_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9.5,
        leading=14,
        textColor=CLR_TEXT_PRI,
        alignment=4,
        spaceAfter=6
    )

    bullet = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=9.5,
        leading=14,
        textColor=CLR_TEXT_PRI,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_header = ParagraphStyle(
        'THead',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=8.5,
        leading=11,
        textColor=CLR_TEXT_PRI
    )

    table_cell = ParagraphStyle(
        'TCell',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=8,
        leading=10.5,
        textColor=CLR_TEXT_PRI
    )

    viva_quote = ParagraphStyle(
        'VivaQuote',
        parent=styles['Normal'],
        fontName=font_italic,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1A365D'),
        leftIndent=12,
        spaceBefore=2,
        spaceAfter=6
    )

    story = []

    # Document Header
    story.append(Paragraph("<b>CYBERSECURITY RISK MANAGEMENT SYSTEM</b>", title_style))
    story.append(Paragraph("Technical Inspiration & Architectural Benchmark Reference", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=CLR_BORDER, spaceBefore=0, spaceAfter=10))

    intro_txt = (
        f"This document provides the technical justification and design origins for the architectural choices "
        f"made in the <b>Cybersecurity Risk Management System (GRC Risk Register)</b> by <b>{STUDENT_NAME}</b> "
        f"(Enrollment No: <b>{ENROLLMENT_NO}</b>). Rather than using legacy paradigms, each core subsystem was "
        f"engineered based on proven design patterns from reputable open-source codebases and recognized industry standards. "
        f"This reference can be submitted alongside the main project report or used during the viva defense."
    )
    story.append(Paragraph(intro_txt, body))
    story.append(Spacer(1, 4))

    # Master Table
    story.append(Paragraph("<b>1. Architectural Benchmark Summary</b>", h1_style))
    matrix_data = [
        [Paragraph("<b>Subsystem</b>", table_header), Paragraph("<b>Your Implementation</b>", table_header), Paragraph("<b>Inspiration Repositories / Standards</b>", table_header), Paragraph("<b>Architectural Benefit</b>", table_header)],
        [
            Paragraph("<b>Server Architecture</b>", table_cell),
            Paragraph("Pure Python 3 Standard Library (<code>http.server</code>, <code>sqlite3</code>)", table_cell),
            Paragraph("<b>Bottle</b> (<code>bottlepy/bottle</code>)<br/><b>CPython BaseHTTP</b>", table_cell),
            Paragraph("Zero <code>pip</code> dependencies, instant local execution, total portability.", table_cell)
        ],
        [
            Paragraph("<b>Risk Calculation Engine</b>", table_cell),
            Paragraph("Deterministic 3x3 matrix ($Score = L \\times I \\in [1, 9]$)", table_cell),
            Paragraph("<b>SimpleRisk</b> (<code>simplerisk/core</code>)<br/><b>NIST SP 800-30</b>", table_cell),
            Paragraph("Eliminates scoring ambiguity; standardizes qualitative severity.", table_cell)
        ],
        [
            Paragraph("<b>Authentication & Security</b>", table_cell),
            Paragraph("Salted PBKDF2-HMAC-SHA256 (100k rounds) + RBAC", table_cell),
            Paragraph("<b>Django Auth</b> (<code>django/django</code>)<br/><b>Passlib</b>", table_cell),
            Paragraph("NIST-compliant password hashing resisting rainbow attacks without external packages.", table_cell)
        ],
        [
            Paragraph("<b>Audit Traceability</b>", table_cell),
            Paragraph("Immutable chronological ledger with foreign user linking", table_cell),
            Paragraph("<b>PaperTrail</b> (<code>paper_trail</code>)<br/><b>Django Simple History</b>", table_cell),
            Paragraph("Complete forensic accountability for regulatory governance.", table_cell)
        ],
        [
            Paragraph("<b>Executive UI & Heatmap</b>", table_cell),
            Paragraph("Vanilla JavaScript SPA with dynamic 3x3 risk matrix", table_cell),
            Paragraph("<b>Tabler</b> (<code>tabler/tabler</code>)<br/><b>AdminLTE</b>", table_cell),
            Paragraph("Responsive, card-based interface providing instant executive visibility.", table_cell)
        ],
    ]
    t_mat = Table(matrix_data, colWidths=[90, 140, 130, 140])
    t_mat.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, CLR_BORDER_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, CLR_BORDER),
        ('BACKGROUND', (0,0), (-1,0), CLR_BG_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_mat)
    story.append(Spacer(1, 8))

    # Detailed Subsystems Breakdown
    story.append(Paragraph("<b>2. Detailed Architectural Subsystems & Viva Explanations</b>", h1_style))

    # 1. Zero-Dependency
    story.append(Paragraph("<b>2.1 Zero-Dependency Server: Inspired by Bottle & CPython Standard Libraries</b>", ParagraphStyle('Sub1', fontName=font_bold, fontSize=10, textColor=CLR_TEXT_PRI, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph(
        "<b>The Problem:</b> Many academic web applications depend on dozens of external packages (Flask, Django, SQLAlchemy), "
        "making deployment fragile and prone to dependency version conflicts.<br/>"
        "<b>The Solution:</b> Inspired by minimalist frameworks like <i>Bottle</i> and CPython's built-in <code>http.server</code>, "
        "the application implements custom request dispatching, JSON serialization, and static routing using only standard Python libraries.",
        body
    ))
    story.append(Paragraph("<b>Viva Defense Tip:</b> <i>\"We adopted Bottle's single-file philosophy to show that robust, secure REST servers can run anywhere without requiring internet access or pip package installation.\"</i>", viva_quote))

    # 2. Risk Calculation
    story.append(Paragraph("<b>2.2 Deterministic Risk Matrix: Inspired by SimpleRisk & NIST SP 800-30</b>", ParagraphStyle('Sub2', fontName=font_bold, fontSize=10, textColor=CLR_TEXT_PRI, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph(
        "<b>The Problem:</b> Spreadsheets and legacy prototypes often calculate risk using arbitrary math or subjective labels with no relational checks.<br/>"
        "<b>The Solution:</b> Following <i>SimpleRisk</i> and NIST SP 800-30, our engine uses standardized integer scales (1 to 3) for Likelihood "
        "and Impact, producing a deterministic score between 1 and 9 categorized into discrete Low (1-2), Medium (3-4), and High (6-9) levels.",
        body
    ))
    story.append(Paragraph("<b>Viva Defense Tip:</b> <i>\"SimpleRisk showed how standardizing qualitative formulas removes human bias from risk evaluation, which we implemented directly in our SQLite database schema.\"</i>", viva_quote))

    # 3. Authentication & RBAC
    story.append(Paragraph("<b>2.3 Cryptographic Security & RBAC: Inspired by Django Contrib Auth</b>", ParagraphStyle('Sub3', fontName=font_bold, fontSize=10, textColor=CLR_TEXT_PRI, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph(
        "<b>The Problem:</b> Many student projects store credentials in plaintext or use deprecated MD5/SHA1 hashing.<br/>"
        "<b>The Solution:</b> Modeled after <i>Django's authentication system</i>, our authentication module uses Python's <code>hashlib.pbkdf2_hmac</code> "
        "with SHA256 and 100,000 iterations combined with 16-byte random salts, alongside strict role separation between Admin and Analyst users.",
        body
    ))
    story.append(Paragraph("<b>Viva Defense Tip:</b> <i>\"We implemented Django's password storage pattern to ensure academic enterprise security standards without introducing heavy external frameworks.\"</i>", viva_quote))

    # 4. Audit Trail
    story.append(Paragraph("<b>2.4 Immutable Audit Ledger: Inspired by PaperTrail & Django Simple History</b>", ParagraphStyle('Sub4', fontName=font_bold, fontSize=10, textColor=CLR_TEXT_PRI, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph(
        "<b>The Problem:</b> Standard CRUD applications overwrite records without leaving an audit trail of who changed what.<br/>"
        "<b>The Solution:</b> Inspired by the <i>PaperTrail</i> design pattern, every database mutation (create, edit, archive) automatically triggers "
        "an append-only audit log recording the action verb, affected entity ID, user ID, and UTC timestamp.",
        body
    ))
    story.append(Paragraph("<b>Viva Defense Tip:</b> <i>\"In enterprise GRC, auditability is essential. PaperTrail's pattern ensures total accountability for compliance verification.\"</i>", viva_quote))

    # 5. UI/UX
    story.append(Paragraph("<b>2.5 Executive Dashboard & Heatmap: Inspired by Tabler & AdminLTE</b>", ParagraphStyle('Sub5', fontName=font_bold, fontSize=10, textColor=CLR_TEXT_PRI, spaceBefore=4, spaceAfter=2)))
    story.append(Paragraph(
        "<b>The Problem:</b> Traditional risk registers present dense, unformatted tables that make executive threat prioritization slow and difficult.<br/>"
        "<b>The Solution:</b> Drawing from <i>Tabler</i>'s modern card-based layouts, the front end provides immediate visual cues through a "
        "dynamic 3x3 risk heatmap, treatment status breakdowns, and high-severity risk badges.",
        body
    ))
    story.append(Paragraph("<b>Viva Defense Tip:</b> <i>\"We used Tabler's dashboard principles to give non-technical decision-makers instant visibility into organizational risk concentration.\"</i>", viva_quote))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Inspiration PDF generated successfully at: {output_pdf}")


if __name__ == "__main__":
    build_inspiration_pdf()
