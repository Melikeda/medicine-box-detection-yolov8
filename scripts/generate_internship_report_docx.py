"""Generate Düzce University CE399/CE499 internship report (Word)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT_DOCS = ROOT / "docs" / "Internship_Report.docx"
OUT_DOWNLOADS = Path.home() / "Downloads" / "Internship_Report_Yolocilin.docx"

YELLOW = "FFF2CC"
ASSETS = ROOT / "docs" / "assets"
SAMPLES = ROOT / "data" / "samples"
DUZCE_LOGO = ASSETS / "duzce-university-logo.png"  # local only; gitignored university mark
FIGURES = ASSETS / "report-figures"


def prepare_figures(lang: str = "en") -> None:
    """Create architecture and catalog charts used in the report body."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    FIGURES.mkdir(parents=True, exist_ok=True)
    tr = lang == "tr"
    plt.rcParams["font.family"] = "DejaVu Sans"

    fig, ax = plt.subplots(figsize=(11.2, 4.4), dpi=170)
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    def box(x, y, w, h, title, lines, facecolor):
        patch = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            linewidth=1.3,
            edgecolor="#1F4E79",
            facecolor=facecolor,
        )
        ax.add_patch(patch)
        ax.text(
            x + w / 2,
            y + h - 0.32,
            title,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#1F4E79",
        )
        ax.text(
            x + w / 2,
            y + h / 2 - 0.12,
            lines,
            ha="center",
            va="center",
            fontsize=8.2,
            color="#333333",
            linespacing=1.35,
        )

    if tr:
        box(0.25, 1.15, 2.35, 2.1, "Flutter", "Yolocilin\nAndroid istemci\ngaleri / kamera", "#E8F4FC")
        box(3.05, 1.15, 2.45, 2.1, "FastAPI", "POST /analyze\nGET /medicines\nPOST /explain, /scans", "#EAF6EA")
        box(5.95, 1.15, 2.55, 2.1, "YZ hattı", "YOLOv8n tespit\nOpenCV + EasyOCR\nRapidFuzz eşleme", "#FFF4E0")
        box(8.95, 1.15, 2.0, 2.1, "SQLite", "1163 ilaç\ntarama geçmişi", "#F6EAF6")
        title = "Yolocilin çalışma yolu"
        stages = ["İlk\nCSV", "TİTCK\n1. tur", "Yenileme", "Marka\ngenişletme", "ATC\ngenişletme"]
        ylabel = "İlaç sayısı"
        chart_title = "Staj süresince ilaç kataloğunun büyümesi"
        fname_pipe = "pipeline_architecture_tr.png"
        fname_cat = "catalog_growth_tr.png"
    else:
        box(0.25, 1.15, 2.35, 2.1, "Flutter app", "Yolocilin\nAndroid client\ngallery / camera", "#E8F4FC")
        box(3.05, 1.15, 2.45, 2.1, "FastAPI", "POST /analyze\nGET /medicines\nPOST /explain, /scans", "#EAF6EA")
        box(5.95, 1.15, 2.55, 2.1, "AI pipeline", "YOLOv8n detect\nOpenCV + EasyOCR\nRapidFuzz match", "#FFF4E0")
        box(8.95, 1.15, 2.0, 2.1, "SQLite", "1163 medicines\nscan history", "#F6EAF6")
        title = "Yolocilin runtime path"
        stages = ["Initial\nCSV", "TİTCK\nround 1", "Refresh", "Brand\nexpand", "ATC\nexpansion"]
        ylabel = "Number of medicines"
        chart_title = "Medicine catalog growth during the internship"
        fname_pipe = "pipeline_architecture.png"
        fname_cat = "catalog_growth.png"

    for x0, x1 in ((2.60, 3.05), (5.50, 5.95), (8.50, 8.95)):
        ax.add_patch(
            FancyArrowPatch(
                (x0, 2.2),
                (x1, 2.2),
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.4,
                color="#1F4E79",
            )
        )

    ax.set_title(title, fontsize=12, color="#1F4E79", pad=6)
    fig.tight_layout()
    fig.savefig(FIGURES / fname_pipe, bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.4, 4.0), dpi=170)
    values = [38, 107, 131, 153, 1163]
    colors = ["#8FB8D6", "#5B93C5", "#3D7BB0", "#2E5F8A", "#1F4E79"]
    bars = ax.bar(stages, values, color=colors, width=0.62)
    ax.set_ylabel(ylabel)
    ax.set_title(chart_title)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 18,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_ylim(0, 1350)
    fig.tight_layout()
    fig.savefig(FIGURES / fname_cat, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def set_run_font(run, *, size=12, bold=False, italic=False, name="Times New Roman"):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def shade_cell(cell, fill=YELLOW):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def set_cell_border(cell):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "000000")
        tc_borders.append(el)
    tc_pr.append(tc_borders)


def add_page_field(paragraph):
    run = paragraph.add_run()
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "end")
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    set_run_font(run, size=12)


def disable_page_numbers(section):
    sect_pr = section._sectPr
    pg_num = OxmlElement("w:pgNumType")
    pg_num.set(qn("w:fmt"), "decimal")
    sect_pr.append(pg_num)


def restart_page_number(section, start=1):
    sect_pr = section._sectPr
    pg_num = OxmlElement("w:pgNumType")
    pg_num.set(qn("w:start"), str(start))
    pg_num.set(qn("w:fmt"), "decimal")
    sect_pr.append(pg_num)


def set_table_borders_none(table):
    tbl_pr = table._tbl.tblPr
    existing = tbl_pr.find(qn("w:tblBorders"))
    if existing is not None:
        tbl_pr.remove(existing)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        el.set(qn("w:sz"), "0")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tbl_pr.append(borders)


def _fill_footer_cell(cell, lines, align):
    cell.text = ""
    for i, (text, size, bold) in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        if not text:
            continue
        r = p.add_run(text)
        set_run_font(r, size=size, bold=bold)


def set_page_border(section):
    """Double frame used in the Düzce booklet: thin outer line, thicker inner line."""
    sect_pr = section._sectPr
    for child in list(sect_pr):
        if child.tag == qn("w:pgBorders"):
            sect_pr.remove(child)
    pg_borders = OxmlElement("w:pgBorders")
    pg_borders.set(qn("w:offsetFrom"), "page")
    pg_borders.set(qn("w:display"), "allPages")
    pg_borders.set(qn("w:zOrder"), "front")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "thinThickSmallGap")
        el.set(qn("w:sz"), "24")
        el.set(qn("w:space"), "22")
        el.set(qn("w:color"), "000000")
        pg_borders.append(el)
    sect_pr.append(pg_borders)


def setup_body_footer(section, lang: str = "en"):
    footer = section.footer
    footer.is_linked_to_previous = False
    p0 = footer.paragraphs[0]
    p0.clear()
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    p0.paragraph_format.line_spacing = 1.0

    table = footer.add_table(1, 3, Cm(16.0))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders_none(table)
    parent = p0._p.getparent()
    parent.remove(table._tbl)
    parent.insert(list(parent).index(p0._p), table._tbl)

    left, mid, right = table.rows[0].cells
    for cell, width in zip((left, mid, right), (Cm(5.5), Cm(5.0), Cm(5.5))):
        cell.width = width

    if lang == "tr":
        _fill_footer_cell(
            left,
            [("Öğrenci: Melike Eda Külahcı", 10, True), ("İmza", 10, False)],
            WD_ALIGN_PARAGRAPH.LEFT,
        )
        _fill_footer_cell(
            right,
            [
                ("Sorumlu Mühendis: Ahmet Mert Özdemir", 10, True),
                ("Ar-Ge Takım Lideri, İmza, Kaşe", 9, False),
            ],
            WD_ALIGN_PARAGRAPH.RIGHT,
        )
        page_label = "Sayfa No: "
    else:
        _fill_footer_cell(
            left,
            [("Student: Melike Eda Külahcı", 10, True), ("Signature", 10, False)],
            WD_ALIGN_PARAGRAPH.LEFT,
        )
        _fill_footer_cell(
            right,
            [
                ("Responsible Engineer: Ahmet Mert Özdemir", 10, True),
                ("R&D Team Leader, Signature, Stamp", 9, False),
            ],
            WD_ALIGN_PARAGRAPH.RIGHT,
        )
        page_label = "Page Number: "

    mid.text = ""
    p_mid = mid.paragraphs[0]
    p_mid.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mid.paragraph_format.space_before = Pt(4)
    p_mid.paragraph_format.space_after = Pt(0)
    p_mid.paragraph_format.line_spacing = 1.0
    r = p_mid.add_run(page_label)
    set_run_font(r, size=11)
    add_page_field(p_mid)


def setup_empty_footer(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.clear()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def configure_section(section):
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(3.6)
    section.header_distance = Cm(1.0)
    section.footer_distance = Cm(0.9)
    set_page_border(section)


class Report:
    def __init__(self):
        self.doc = Document()
        style = self.doc.styles["Normal"]
        style.font.name = "Times New Roman"
        style.font.size = Pt(12)
        style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        pf = style.paragraph_format
        pf.line_spacing = 1.5
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        configure_section(self.doc.sections[0])
        setup_empty_footer(self.doc.sections[0])

    def _p(self, *, align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.5, indent=True, space_before=0, space_after=0):
        p = self.doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = spacing
        p.paragraph_format.line_spacing_rule = (
            WD_LINE_SPACING.ONE_POINT_FIVE if spacing == 1.5 else WD_LINE_SPACING.SINGLE
        )
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.first_line_indent = Cm(1.25) if indent else Cm(0)
        return p

    def body(self, text, *, first=False):
        p = self._p(indent=not first)
        r = p.add_run(text)
        set_run_font(r)
        return p

    def h1(self, text):
        p = self._p(align=WD_ALIGN_PARAGRAPH.LEFT, indent=False, space_before=12, space_after=6)
        r = p.add_run(text.upper())
        set_run_font(r, bold=True)
        return p

    def h2(self, text):
        p = self._p(align=WD_ALIGN_PARAGRAPH.LEFT, indent=False, space_before=10, space_after=4)
        r = p.add_run(text)
        set_run_font(r, bold=True)
        return p

    def caption(self, text, *, above=False):
        p = self._p(align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, indent=False, space_before=6, space_after=6)
        r = p.add_run(text)
        set_run_font(r, size=12)
        return p

    def fill_line(self, label, blank="________________________________"):
        p = self._p(align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.5, indent=False, space_before=2, space_after=2)
        r = p.add_run(f"{label} ")
        set_run_font(r, bold=True)
        r2 = p.add_run(blank)
        set_run_font(r2)
        r2.font.highlight_color = WD_COLOR_INDEX.YELLOW
        return p

    def mono(self, text):
        return self.code(text)

    def code(self, text):
        table = self.doc.add_table(rows=1, cols=1)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        shade_cell(cell, fill="F4F4F4")
        set_cell_border(cell)
        cell.text = ""
        lines = text.split("\n")
        first = cell.paragraphs[0]
        first.paragraph_format.line_spacing = 1.0
        first.paragraph_format.space_before = Pt(6)
        first.paragraph_format.space_after = Pt(0)
        first.paragraph_format.left_indent = Cm(0.15)
        r = first.add_run(lines[0] if lines else "")
        set_run_font(r, size=8.5, name="Courier New")
        for line in lines[1:]:
            p = cell.add_paragraph()
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.left_indent = Cm(0.15)
            run = p.add_run(line)
            set_run_font(run, size=8.5, name="Courier New")
        if cell.paragraphs:
            cell.paragraphs[-1].paragraph_format.space_after = Pt(6)
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(4)
        return table

    def bullets(self, items):
        for item in items:
            p = self.doc.add_paragraph(style="List Bullet")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            if p.runs:
                p.runs[0].text = item
                set_run_font(p.runs[0])
            else:
                r = p.add_run(item)
                set_run_font(r)

    def numbered(self, items):
        for item in items:
            p = self.doc.add_paragraph(style="List Number")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            if p.runs:
                p.runs[0].text = item
                set_run_font(p.runs[0])
            else:
                r = p.add_run(item)
                set_run_font(r)

    def table(self, headers, rows, fill_cols=None):  # fill_cols kept for call-site compatibility; highlighting uses "____" in cell text
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(h)
            set_run_font(r, size=11, bold=True)
        for ri, row in enumerate(rows):
            for ci, val in enumerate(row):
                cell = table.rows[ri + 1].cells[ci]
                cell.text = ""
                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.0
                r = p.add_run(str(val))
                set_run_font(r, size=11)
                if "____" in str(val):
                    shade_cell(cell)
                    r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        self.doc.add_paragraph().paragraph_format.space_after = Pt(0)
        return table

    def image(self, path: Path, width_cm=14.0):
        if not path.exists():
            return
        p = self._p(align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, indent=False, space_before=6, space_after=4)
        run = p.add_run()
        run.add_picture(str(path), width=Cm(width_cm))

    def page_break(self):
        self.doc.add_page_break()

    def add_section_break(self):
        self.doc.add_section()
        configure_section(self.doc.sections[-1])


def build():
    prepare_figures()
    rep = Report()
    doc = rep.doc

    # ----- COVER (no page number; logo + page frame like the booklet) -----
    if DUZCE_LOGO.exists():
        p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, indent=False, space_before=6, space_after=8)
        run = p.add_run()
        run.add_picture(str(DUZCE_LOGO), width=Cm(4.6))

    for line in (
        "DUZCE UNIVERSITY",
        "FACULTY OF ENGINEERING",
        "COMPUTER ENGINEERING DEPARTMENT",
    ):
        p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=0, space_after=0)
        r = p.add_run(line)
        set_run_font(r, size=16, bold=True)

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=24, space_after=12)
    r = p.add_run("Internship Report")
    set_run_font(r, size=18, bold=True)

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=6, space_after=18)
    r = p.add_run("Yolocilin — Medicine Box Detection, Identification and Information System")
    set_run_font(r, size=14, bold=True)

    cover_fields = [
        ("Student ID:", "221015057"),
        ("Name Surname:", "Melike Eda Külahcı"),
        ("Department:", "Computer Engineering"),
        ("Lecture Code:", "CE499"),
        ("Internship Dates:", "29.07.2026 – 03.08.2026"),
        ("Host Company:", "Cerebrum Tech"),
    ]
    for label, value in cover_fields:
        p = rep._p(align=WD_ALIGN_PARAGRAPH.LEFT, indent=False, space_before=4, space_after=4)
        p.paragraph_format.left_indent = Cm(2.5)
        r = p.add_run(f"{label}  ")
        set_run_font(r, size=12, bold=True)
        r2 = p.add_run(value)
        set_run_font(r2, size=12)

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=36)
    r = p.add_run("Düzce, 2026")
    set_run_font(r, size=12)

    # ----- CONTENTS -----
    rep.add_section_break()
    setup_empty_footer(doc.sections[-1])

    p = rep._p(align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, space_before=0, space_after=12)
    r = p.add_run("CONTENTS")
    set_run_font(r, size=16, bold=True)

    toc = [
        (14, "1. INTRODUCTION", True),
        (14, "2. INFORMATION ABOUT THE COMPANY", True),
        (12, "    2.1 Name, Address and Field of Activity", False),
        (12, "    2.2 Personnel and Organization", False),
        (12, "    2.3 Contact Person", False),
        (14, "3. DESCRIPTION OF THE PROJECT AND THE WORK TO BE DONE", True),
        (12, "    3.1 Problem Definition", False),
        (12, "    3.2 Planned Work", False),
        (12, "    3.3 Technologies Used", False),
        (12, "    3.4 Scope Limits", False),
        (14, "4. PROJECT AND WORK DONE", True),
        (12, "    4.1 Position and Tasks During the Internship", False),
        (12, "    4.2 Project Purpose and Analysis", False),
        (12, "    4.3 Requirements", False),
        (12, "    4.4 Design and Architecture", False),
        (12, "    4.5 Dataset and YOLOv8 Training", False),
        (12, "    4.6 Object Detection", False),
        (12, "    4.7 Image Preprocessing and OCR", False),
        (12, "    4.8 Matching Algorithms and Business Rules", False),
        (12, "    4.9 Database", False),
        (12, "    4.10 Backend API", False),
        (12, "    4.11 Authentication and Authorization", False),
        (12, "    4.12 Mobile Application", False),
        (12, "    4.13 Validation, Testing and Performance", False),
        (12, "    4.14 Security and DevOps", False),
        (12, "    4.15 Problems Encountered and Solutions", False),
        (12, "    4.16 Documentation and Publication (GitHub, Kaggle, Medium)", False),
        (14, "5. CONCLUSION", True),
        (14, "APPENDIXES", True),
        (12, "    Appendix A  OpenCV Preprocessing (CLAHE and sharpening)", False),
        (12, "    Appendix B  YOLO Confidence Fallback", False),
        (12, "    Appendix C  Fast-Mode OCR Variants", False),
        (12, "    Appendix D  RapidFuzz Matching", False),
        (12, "    Appendix E  Analyze Upload Path", False),
        (12, "    Appendix F  Security Headers", False),
        (12, "    Appendix G  Sample photographs (see Section 4)", False),
        (14, "RESOURCES", True),
    ]
    for size, title, bold in toc:
        p = rep._p(align=WD_ALIGN_PARAGRAPH.LEFT, spacing=1.0, indent=False, space_before=2, space_after=2)
        r = p.add_run(title)
        set_run_font(r, size=size, bold=bold)

    # ----- BODY: page numbering starts -----
    rep.add_section_break()
    restart_page_number(doc.sections[-1], 1)
    setup_body_footer(doc.sections[-1])

    # 1. INTRODUCTION
    rep.h1("1. INTRODUCTION")
    rep.body(
        "This report was prepared for the Computer Engineering internship course "
        "CE499 at Düzce University Faculty of Engineering. The internship was "
        "completed at Cerebrum Tech in Ankara, at the Cyberpark office, between "
        "29.07.2026 and 03.08.2026. The host company works on artificial intelligence, "
        "computer vision, natural language processing and predictive analytics [1], [2].",
        first=True,
    )
    rep.body(
        "The internship produced a working software product. The product is named "
        "Yolocilin. The same name is used for the Android application, the GitHub "
        "repository, the GitHub Projects board and the Kaggle dataset. A user "
        "photographs one or more medicine boxes with the Android application. The "
        "FastAPI backend detects each box with YOLOv8n, reads the printed text with "
        "OpenCV preprocessing and EasyOCR, and matches the noisy text against a catalog "
        "of 1163 medicines using RapidFuzz. Results are shown in the application. After "
        "a successful match, a short explanation can be requested from Google Gemini. "
        "Scan history is stored on the device and, when the server is reachable, copied "
        "to the backend as JSON."
    )
    rep.body(
        "Yolocilin is not a clinical decision tool. The API response and the result "
        "screen state that the output is not medical advice and that the user should "
        "confirm information with the official leaflet or a pharmacist. The language "
        "model is therefore kept on a separate endpoint, and the prompt is limited to "
        "catalog fields."
    )
    rep.body(
        "Work started from the dataset and model training, then continued with "
        "preprocessing, OCR, matching, the REST API, SQLite, Docker, GitHub Actions "
        "and the Flutter client. Later phases added production-oriented controls, "
        "catalog expansion from the TİTCK SKRS list, optional Gemini explanations, "
        "camera capture and scan history. Methods learned during development were also "
        "recorded in three Medium series that follow the layers of the product [30], "
        "[31], [32]."
    )
    rep.body(
        "Section 2 gives company information. Section 3 defines the project and the "
        "planned work. Section 4 describes how the system was built, tested and "
        "corrected after real photographs failed. Section 5 collects the results. The "
        "full source code is in the GitHub repository [33]. The Appendixes contain only "
        "short excerpts that illustrate the decisions discussed in the body."
    )

    # 2. COMPANY
    rep.h1("2. INFORMATION ABOUT THE COMPANY")
    rep.body(
        "The figures in this section come from the internship workplace form and from "
        "the public company website [1], [2].",
        first=True,
    )

    rep.h2("2.1 Name, Address and Field of Activity")
    rep.body(
        "The host company is Cerebrum Tech. The internship workplace address is "
        "Ankara Teknoloji Geliştirme Bölgesi, Üniversiteler Mahallesi, 1606. Cadde, "
        "Kapı No: 4/A, Cyberpark A Blok, 7. Kat No: 707, 06800 Bilkent, Çankaya / "
        "Ankara. The service area is software development. The internship was "
        "completed in the R&D (Ar-Ge) department."
    )
    rep.body(
        "Cerebrum Tech is an artificial-intelligence firm working on computer vision, "
        "natural language processing and predictive analytics [1]. Public pages also "
        "mention forest-fire detection and smart agriculture tools [3]. Yolocilin is "
        "the medicine-box detection, identification and information system built during "
        "the internship. It is a self-contained R&D delivery, independent of the "
        "company’s published product lines."
    )
    rep.body(
        "The company is based in Ankara. The public team page lists Dr. R. Erdem Erkul "
        "as Founder and Chairman [4]."
    )

    rep.h2("2.2 Personnel and Organization")
    rep.body(
        "According to the workplace form the company has 10 engineers, 3 finance staff "
        "and 17 other employees, 30 people in total. The intern reported to Ahmet Mert "
        "Özdemir, R&D Team Leader."
    )
    rep.caption(
        "Table 2.1 Workplace information used in this report.",
        above=True,
    )
    rep.table(
        ["Item", "Value"],
        [
            ["Company name", "Cerebrum Tech"],
            ["Department", "R&D (Ar-Ge)"],
            ["Engineers", "10"],
            ["Finance staff", "3"],
            ["Other staff", "17"],
            ["Total staff", "30"],
            ["Company supervisor", "Ahmet Mert Özdemir"],
            ["Supervisor title", "R&D Team Leader"],
            ["Intern position", "Intern, R&D department"],
        ],
    )

    rep.h2("2.3 Contact Person")
    rep.caption(
        "Table 2.2 Contact person named on the internship workplace form.",
        above=True,
    )
    rep.table(
        ["Item", "Value"],
        [
            ["Name and surname", "Ahmet Mert Özdemir"],
            ["Position", "R&D Team Leader"],
            ["Telephone", "0312 544 50 50"],
            ["E-mail", "info@cerebrumtechnologies.co"],
            ["Website", "https://www.cerebrumtechnologies.com"],
        ],
    )

    # 3. DESCRIPTION
    rep.h1("3. DESCRIPTION OF THE PROJECT AND THE WORK TO BE DONE")
    rep.h2("3.1 Problem Definition")
    rep.body(
        "Identifying a medicine from a phone photograph is unreliable if it is done "
        "by guessing the brand. Packaging may be rotated, partly out of frame, or "
        "printed in a mix of Turkish and English. One photo may contain several boxes. "
        "OCR on a raw image produces noisy strings such as afern, fen, ibucold €, or "
        "dosage lines like 250 mo / j0o mo tablot. Matching those strings to a brand "
        "list without extra checks can return the wrong drug, which is worse than "
        "returning not found.",
        first=True,
    )
    rep.body("The internship project was defined as a working system that:")
    rep.numbered(
        [
            "detects every medicine box in a photo,",
            "reads the print on each crop,",
            "matches the text to a seed catalog,",
            "returns a structured JSON result to an Android application,",
            "optionally explains a matched drug in short Turkish or English text,",
            "keeps a history of successful scans.",
        ]
    )

    rep.h2("3.2 Planned Work")
    rep.body(
        "The work was split into sequential phases. Each later phase used a Git "
        "feature branch and a GitHub issue. The planned order was: repository and "
        "environment setup; dataset and Roboflow annotation; YOLOv8n training; "
        "OpenCV preprocessing and EasyOCR; RapidFuzz matching against a CSV catalog; "
        "a unified pipeline service layer; FastAPI (health, analyze, later medicines, "
        "explain, scans); SQLite as the runtime catalog; automated tests, Docker and "
        "GitHub Actions; Flutter Android client (gallery, then camera); catalog "
        "expansion from TİTCK SKRS; then CPU performance work, production hardening, "
        "Gemini explanations, scan history, end-to-end tooling; a PaddleOCR trial "
        "(not adopted); and tighter matching so suffix OCR cannot open a wrong drug card."
    )
    rep.body(
        "An early idea of a Streamlit web interface was dropped. GitHub issue #7 was "
        "closed in favour of Flutter and FastAPI so that the internship delivery would "
        "look like a mobile product with a real HTTP contract rather than a notebook demo."
    )

    rep.h2("3.3 Technologies Used")
    rep.body(
        "Table 3.1 lists only technologies that exist in the repository "
        "(requirements.txt, pubspec.yaml, Docker files, and source). Items that remain "
        "on the roadmap (PostgreSQL, iOS client, public HTTPS hosting, per-user "
        "accounts) are not presented as implemented."
    )
    rep.caption(
        "Table 3.1 Technologies actually used in Yolocilin and the role of each layer.",
        above=True,
    )
    rep.table(
        ["Layer", "Technology", "Role"],
        [
            ["Language (AI and API)", "Python 3.11+ (CI 3.11, Docker 3.12)", "Pipeline and FastAPI"],
            ["Detection", "YOLOv8n, Ultralytics 8.4.87, PyTorch 2.12.1", "Single-class medicine-box detector"],
            ["Image processing", "OpenCV, Pillow", "Crop, resize, CLAHE, threshold, OCR variants"],
            ["OCR", "EasyOCR 1.7.2 (tr, en)", "Text from cropped boxes; PaddleOCR tried, not adopted"],
            ["Matching", "RapidFuzz 3.14.5 (fuzz.WRatio)", "Noisy OCR to catalog row"],
            ["Catalog seed", "CSV (medicines.csv)", "Source of truth, 1163 rows"],
            ["Runtime database", "SQLite via SQLAlchemy 2.0.46", "medicines and scans tables"],
            ["Official enrichment", "TİTCK SKRS XLSX (pandas, openpyxl)", "Dosage, form, ingredient, brand expansion"],
            ["Backend", "FastAPI 0.140.0, Uvicorn, Pydantic Settings", "REST API"],
            ["LLM (optional)", "google-genai 1.16.1, Gemini Flash", "POST /api/v1/explain"],
            ["Mobile", "Flutter 3.19+, Dart SDK ≥ 3.3", "Android client Yolocilin"],
            ["Mobile storage", "sqflite, shared_preferences", "Local history and OCR-mode preference"],
            ["Mobile HTTP / camera", "http, image_picker", "Multipart upload, gallery and camera"],
            ["Tests", "pytest 8.4.2, httpx, Flutter test", "Backend and widget tests"],
            ["Containers", "Docker, docker-compose", "API image python:3.12-slim-bookworm"],
            ["CI", "GitHub Actions", "Backend tests, mobile tests, Docker build"],
            ["Dataset tooling", "Roboflow", "Annotation and YOLO export"],
            ["Dataset publish", "Kaggle, CC BY 4.0", "395 privacy-cleaned images"],
        ],
    )

    rep.h2("3.4 Scope Limits")
    rep.body(
        "The following items are stated as not implemented in the code and roadmap: "
        "end-user login, JWT or private per-user scan lists (server scans are a global "
        "list); an admin panel; an iOS client; PostgreSQL; a barcode or QR path; a "
        "public cloud HTTPS deployment; WAF or DDoS protection; a cloud secret manager "
        "for the Gemini key. There is no login screen. The mobile flow is splash, home "
        "(welcome / scan / history), image preview, then result."
    )
    rep.image(ASSETS / "yolocilin-banner.png", 14.0)
    rep.caption(
        "Figure 3.1 Yolocilin product banner. The same name is used for the Android "
        "application, the GitHub repository (github.com/Melikeda/yolocilin) and the "
        "Kaggle dataset."
    )

    # 4. PROJECT AND WORK DONE
    rep.h1("4. PROJECT AND WORK DONE")
    rep.body(
        "This section is the technical record of the internship. Thresholds and counts "
        "are taken from the current source (src/services/config.py, backend/app/config.py, "
        "catalog README).",
        first=True,
    )

    rep.h2("4.1 Position and Tasks During the Internship")
    rep.body(
        "The intern worked in the R&D department under Ahmet Mert Özdemir, R&D Team "
        "Leader. The daily work followed a feature-branch workflow: one focused change, "
        "one branch, one pull request, merge to main. Progress was tracked on a GitHub "
        "Projects board with Todo, In Progress and Done columns. Tasks included collecting and "
        "annotating medicine-box images; training YOLOv8n; writing OpenCV modules and "
        "EasyOCR pipelines; implementing RapidFuzz matching and later reliability "
        "guards; building the FastAPI analyze, medicines, explain and scans endpoints; "
        "seeding SQLite from CSV; expanding the catalog from TİTCK SKRS; writing "
        "pytest and Flutter tests; packaging the API with Docker; configuring GitHub "
        "Actions; implementing the Android client (gallery, camera, bilingual UI, "
        "history); and hardening production settings (CORS, rate limits, magic-byte "
        "upload checks). Related code is in the Appendixes, not in this section."
    )

    rep.h2("4.2 Project Purpose and Analysis")
    rep.body(
        "Yolocilin answers a practical question: given a phone photo of one or more "
        "medicine boxes, which catalog entries, if any, do those boxes correspond to? "
        "The system has three cooperating parts. The src package contains detection, "
        "preprocessing, OCR, matching and SQLAlchemy models. The backend/app package "
        "contains FastAPI routers, validation, rate limits, the LLM service and scan "
        "services. The mobile package is the Flutter Android UI. A parallel examples "
        "tree holds learning scripts; production code does not import those scripts."
    )
    rep.body(
        "Analysis followed the pipeline order. Medicine-box photos were annotated in "
        "Roboflow as a single class medicine-box. An earlier internal split had 478 "
        "images. Before the public Kaggle release, third-party screenshots and frames "
        "with handwritten personal notes were removed. The published set is 395 images: "
        "train 363, valid 15, test 17, license CC BY 4.0 [5]. Training used "
        "src/train.py: Ultralytics YOLOv8n from yolov8n.pt, 50 epochs, image size 640, "
        "batch 8, device CPU [6], [7], [8]. On clear test shots, box confidences were "
        "typically between 0.80 and 0.93. Failures clustered on low light and partly "
        "visible boxes, which later motivated the 0.40 / 0.25 confidence fallback."
    )
    rep.body(
        "EasyOCR on a single raw crop was not enough. Several preprocessed variants "
        "were generated per crop. A fast mode was added when CPU latency became "
        "unusable on the emulator. RapidFuzz WRatio scored short garbage highly and "
        "confused dosage lines with active-ingredient fields. After the catalog grew, "
        "a missing brand could still land on a neighbour. Matching therefore gained a "
        "stack of guards instead of a single cutoff [11]."
    )

    rep.h2("4.3 Requirements")
    rep.body(
        "Requirements lived in GitHub issues, the roadmap and the API schemas."
    )
    p = rep._p(indent=False)
    r = p.add_run("Functional requirements.")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        " Detect all medicine boxes in an uploaded JPEG, PNG, WebP or BMP file "
        "(maximum 10 MB). Support more than one box in the same photo. Read Turkish "
        "and English print. Match against medicine_name, brand_name and, when safe, "
        "active_ingredient. Return per-box status matched, not_found, not_medicine_box "
        "or error. Expose catalog search. Optionally explain a matched medicine_id. "
        "Provide an Android client with gallery and camera, bilingual UI, result cards, "
        "local history (cap 50) and best-effort server sync when reachable (cap 200). Expose a health "
        "endpoint that reports whether models are loaded."
    )
    set_run_font(r2)
    p = rep._p(indent=False)
    r = p.add_run("Non-functional requirements.")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        " Load YOLO and EasyOCR once at process start. Run the blocking pipeline in "
        "asyncio.to_thread. Default OCR mode fast; accurate available as a query flag. "
        "In production, reject wildcard CORS, disable /docs, mask 500 details and keep "
        "rate limits on. Never commit secrets. Show a medical disclaimer on analyze "
        "responses and on the result screen."
    )
    set_run_font(r2)

    rep.h2("4.4 Design and Architecture")
    rep.body(
        "The design rule that mattered most was modularity with a single orchestration "
        "point. PipelineManager.load() creates one YOLO model, one EasyOCR reader and "
        "one matching service. analyze_all(image_path) then runs detection, OCR and "
        "matching and attaches per-stage timings (yolo_ms, ocr_ms, matching_ms, "
        "total_ms). FastAPI’s lifespan hook loads those services at startup and unloads "
        "them on shutdown so tests can isolate state [12], [13]."
    )
    rep.mono(
        "Yolocilin (Flutter, Android)\n"
        "        |  gallery or camera\n"
        "        v\n"
        "POST /api/v1/analyze?mode=fast|accurate\n"
        "        |\n"
        "        v\n"
        "FastAPI  ->  PipelineManager (YOLO + EasyOCR loaded once)\n"
        "        |\n"
        "        v\n"
        "YOLOv8 detect -> crop -> OpenCV variants -> EasyOCR\n"
        "        -> normalize -> RapidFuzz -> SQLite catalog (1163)\n"
        "        |\n"
        "        v\n"
        "JSON (per-box status + summary + timing + disclaimer)\n"
        "        |-- local sqflite history + POST /api/v1/scans when reachable\n"
        "        +-- optional POST /api/v1/explain -> Gemini"
    )
    rep.caption(
        "Figure 4.1 Runtime path from the Android client through the analyze pipeline. "
        "Models are loaded at API startup, not per request. Explain is a separate call "
        "so that Gemini does not add latency to OCR."
    )
    rep.mono(
        "mobile/lib  (screens, services, models)\n"
        "        | HTTP multipart / JSON\n"
        "        v\n"
        "backend/app  (routers, middleware, services)\n"
        "        |\n"
        "        v\n"
        "src/services  PipelineManager -> Detection / OCR / Matching\n"
        "        |\n"
        "        v\n"
        "SQLite medicines.db (medicines + scans)\n"
        "CSV     medicines.csv (seed; upserted at start)"
    )
    rep.caption(
        "Figure 4.2 Component boundaries. The mobile application does not embed the "
        "medicine catalog. Local scan_history.db stores analyze JSON and a copy of the "
        "photo. The server scans table stores JSON only, not images."
    )
    rep.image(FIGURES / "pipeline_architecture.png", 15.5)
    rep.caption(
        "Figure 4.3 System architecture drawn from the implemented modules. The Flutter "
        "client sends a photograph to FastAPI; the pipeline runs YOLOv8, OCR and "
        "RapidFuzz against the SQLite catalog of 1163 medicines."
    )

    rep.h2("4.5 Dataset and YOLOv8 Training")
    rep.body(
        "Images were first kept as a bounding-box table: filename, width, height, "
        "class and xmin / ymin / xmax / ymax corners. That table is an intermediate "
        "annotation format. A brand name (for example Aferin or Parol) is not a detector "
        "class; the brand is found later by OCR and catalog matching. For training, the "
        "records were merged in Roboflow as a single class medicine-box and exported to "
        "YOLO format: one text file per image, class id 0, normalized center and size. "
        "data/dataset/data.yaml sets nc: 1 and the class name medicine-box [22]."
    )
    rep.caption(
        "Table 4.1 Fields of the bounding-box annotation table. This table is separate "
        "from the medicines.csv catalog expansion.",
        above=True,
    )
    rep.table(
        ["Field", "Meaning"],
        [
            ["filename", "Image file name"],
            ["width, height", "Image size in pixels"],
            ["class", "Object class; medicine-box in training"],
            ["xmin, ymin", "Top-left corner of the box"],
            ["xmax, ymax", "Bottom-right corner of the box"],
        ],
    )
    rep.body(
        "An earlier internal split had 478 images. Before the Kaggle release, third-party "
        "screenshots and frames with handwritten notes were removed. The cleaned set was "
        "published on Kaggle as Yolocilin Medicine Box Detection: 395 images (train 363, "
        "valid 15, test 17), license CC BY 4.0 [5]. The aim was a reproducible download "
        "without committing training images to Git."
    )
    rep.body(
        "Training used src/train.py: Ultralytics YOLOv8n from yolov8n.pt, 50 epochs, "
        "image size 640, batch 8, device CPU [6], [7], [8]. YOLOv8 Nano was used because "
        "the intern machine ran CPU inference and the task is a single large object class. "
        "Weights are not committed. The API resolves best.pt from common runs/detect "
        "layouts, models/best.pt, or YOLO_MODEL_PATH. On clear test shots, box confidences "
        "were typically between 0.80 and 0.93. Failures on low light and partly visible "
        "boxes motivated the 0.40 / 0.25 confidence fallback."
    )
    rep.caption(
        "Table 4.2 YOLOv8n training configuration used in src/train.py.",
        above=True,
    )
    rep.table(
        ["Parameter", "Value"],
        [
            ["Model", "YOLOv8n (yolov8n.pt, transfer learning)"],
            ["Epochs", "50"],
            ["Image size", "640 x 640"],
            ["Batch size", "8"],
            ["Device", "CPU"],
            ["Published images (Kaggle)", "395 (train 363, valid 15, test 17)"],
            ["License", "CC BY 4.0"],
        ],
    )
    rep.image(SAMPLES / "aferin_forte.jpg", 10.5)
    rep.caption(
        "Figure 4.4 Single-box sample used in intern tests (A-Ferin Forte). Text on "
        "the package is readable; this is the kind of input the detector and OCR path "
        "were checked against."
    )
    rep.image(SAMPLES / "imunol_defence.jpg", 10.0)
    rep.caption(
        "Figure 4.5 Second single-box sample (İmunol Defence). A different layout and "
        "colour scheme was useful for checking that matching is not limited to one brand."
    )
    rep.image(SAMPLES / "2li_ornek.png", 10.5)
    rep.caption(
        "Figure 4.6 Two-box sample (Aferin and Dolorex). The detector is required to "
        "return one crop per box; each crop is matched independently."
    )

    rep.h2("4.6 Object Detection")
    rep.body(
        "DetectionService.detect_all runs YOLO twice when needed. The primary "
        "confidence is 0.40. If that pass is empty, or if the best score is below 0.55 "
        "and a 0.25 pass finds more boxes, the fallback result is kept. On a blurry "
        "multi-box photo, intern testing recorded 0 boxes at the old 0.60 threshold and "
        "3 boxes after fallback. YOLO false positives are not removed at the detector. "
        "They are classified later as not_medicine_box when OCR and matching look "
        "implausible (score below minimum_plausible_match_score 65, empty or garbage "
        "text, or text that is not a valid name candidate). The related listing is "
        "Appendix B."
    )
    rep.caption(
        "Table 4.3 Detection thresholds currently set in PipelineConfig.",
        above=True,
    )
    rep.table(
        ["Setting", "Value", "Meaning"],
        [
            ["Primary confidence", "0.40", "First pass"],
            ["Fallback confidence", "0.25", "Retry if the first pass is empty or weak"],
            ["Weak-detection rule", "max confidence < 0.55", "Use fallback if it finds more boxes"],
        ],
    )

    rep.h2("4.7 Image Preprocessing and OCR")
    rep.body(
        "Two preprocessing layers exist. The package src/preprocessing is the reusable "
        "OpenCV layer: grayscale, resize, crop, median blur, CLAHE, adaptive threshold, "
        "opening and closing [9]. The OCR runtime does not stop at that single binary "
        "pipeline. src/ocr/ocr_pipeline.py builds a dictionary of variants per crop: "
        "rotation by 0, 90, 180 and 270 degrees; cubic upscale (1.75 times in fast mode, "
        "2.0 times in accurate mode); in fast mode, original colour and sharpened only; "
        "in accurate mode, unsharp, CLAHE, CLAHE plus sharpen, Otsu, and extra blur "
        "variants if Laplacian variance is below 80 [10]."
    )
    rep.body(
        "Before the pipeline starts, the server downscales the upload so the long edge "
        "is at most 1280 pixels. The Flutter gallery picker also compresses to a maximum "
        "of 1280 pixels at quality 65 percent. Those two resizes are the main reason "
        "later analyze runs are closer to one to three minutes on CPU than the first "
        "emulator measurement of about 255 seconds."
    )
    rep.caption(
        "Table 4.4 OCR modes in the current PipelineConfig.",
        above=True,
    )
    rep.table(
        ["Mode", "Behaviour"],
        [
            [
                "fast (API default)",
                "Scale 1.75x, four rotations, 2 variants per angle (up to 8 OCR passes), early exit only at score ≥ 95",
            ],
            [
                "accurate",
                "Scale 2.0x, four rotations, full variant set (about 52 passes on difficult crops), no early exit",
            ],
        ],
    )
    rep.body(
        "EasyOCR is created once with languages tr and en. GPU is off by default. "
        "Adjacent OCR tokens are combined so that ibucold and € can become ibucold c. "
        "Generic phrases and dosage-only lines are dropped before RapidFuzz. CLAHE and "
        "sharpening are listed in Appendix A; fast-mode variants are in Appendix C."
    )
    rep.body(
        "PaddleOCR was also run on the same YOLO crops. On Turkish box photos it was "
        "not a net accuracy win, it was slower on CPU, and it added Windows operational "
        "cost. Production OCR stayed EasyOCR [10], [33]. Wall-clock wait is almost "
        "entirely EasyOCR on CPU; YOLO and catalog matching are milliseconds to a "
        "second. Blurry, distant or multi-box shots may run 8 variants then a 24-variant "
        "deep retry; that limit is expected with the internship hardware."
    )

    rep.h2("4.8 Matching Algorithms and Business Rules")
    rep.body(
        "Matching changed the most after real photographs were tried. The core score is "
        "RapidFuzz fuzz.WRatio on normalized strings, range 0 to 100 [11]. "
        "Normalization lowercases, collapses whitespace, and maps €, © and ¢ to c, "
        "because the Ibucold C box was read as ibucold €. For each OCR candidate the "
        "matcher compares medicine_name, brand_name and active_ingredient, then keeps "
        "the best score. Several rules can discard that winner."
    )
    rep.caption(
        "Table 4.5 Matching guards. The final accept cutoff is 88. Fast OCR early-exit "
        "stops only when the score is at least 95.",
        above=True,
    )
    rep.table(
        ["Rule", "Threshold or behaviour", "Why it exists"],
        [
            ["Minimum match score", "88", "After catalog growth, 80 still accepted wrong neighbours"],
            ["Name coverage ratio", "0.55", "Blocks one-letter false positives"],
            ["Partial brand coverage", "prefix fragment ≥ 5 letters, coverage 0.55; suffix rejected", "fen/alm/pal must not become a drug card"],
            ["Generic single words", "forte, plus, tablet, şurup, …", "Those tokens appear on many boxes"],
            ["Generic active ingredients", "ibuprofen, paracetamol, … as the only token", "Cannot choose Nurofen versus Brufen"],
            ["Active-ingredient-only match", "discarded if name/brand scores stay below 65", "Parafon was matching Nurofen via the ingredient field"],
            ["Dosage or form only", "mg, ml, tablet, tablot, … without a brand-like token", "250 mo / j0o mo tablot is not a brand"],
            ["Label token overlap", "shared token of at least 4 letters", "Missing-catalog OCR must return not_found"],
            ["Foreign brand token", "long OCR token absent from candidate labels", "Endofer-like text must not map to Coldaway C"],
            ["Brand-family disambiguation", "Plus / Forte / Jel / Gargara tokens", "Same score must not prefer the longer SKU name by default"],
            ["Fast OCR early-exit", "score ≥ 95", "An 88 suffix guess must not stop remaining variants"],
        ],
    )
    rep.body(
        "Per-box status values are matched (reliable score and guards passed), "
        "not_found (packaging looks like a medicine box but no catalog row is safe), "
        "not_medicine_box (YOLO crop failed plausibility checks), and error (exception "
        "on that crop). Brand-family logic lives in src/matching/brand_disambiguation.py. "
        "Parol versus Parol Plus is decided by whether OCR actually contains plus, not "
        "by longer name wins. Exact short brands such as Etol still match. Suffix "
        "fragments (fen, alm, pal) are not a match; the product prefers not_found "
        "(PR #67, repository Report 27) [33]. The related listing is Appendix D."
    )

    rep.h2("4.9 Database")
    rep.body(
        "The project uses two table families. The first is image annotation (Section 4.5, "
        "Table 4.1). The second is the medicine catalog: data/database/medicines.csv. "
        "The catalog is the source matched against OCR output; it is not the annotation "
        "CSV. At runtime SQLAlchemy maps two tables in medicines.db [14], [15]. "
        "ensure_database_seeded() upserts CSV into SQLite on startup. Editing SQLite by "
        "hand is wrong; the next seed overwrites it. TİTCK SKRS downloaded on 06.08.2026 "
        "listed 7948 active product rows [21]. The intern catalog is a curated subset: "
        "high-use brands, ATC group fill, and manual OTC rows such as Mucosolvan, Redoxon "
        "and Strepsils. Placeholder rate on dosage, form and ingredient is about 7 to 11 "
        "percent, with a CI gate of less than 15 percent. pytest requires at least 900 "
        "rows and zero duplicate identifiers."
    )
    rep.caption(
        "Table 4.6 Catalog growth during the internship (committed CSV, not the full SKRS dump).",
        above=True,
    )
    rep.table(
        ["Stage", "Rows"],
        [
            ["Early matching tests", "38"],
            ["First TİTCK enrichment (Issue #41)", "107"],
            ["Final-polish refresh (06.08.2026)", "131"],
            ["Controlled extra brands (Ferrum, Buscopan, …)", "153"],
            ["Popular TR / ATC expansion (PR #59)", "1163"],
        ],
    )
    rep.image(FIGURES / "catalog_growth.png", 14.0)
    rep.caption(
        "Figure 4.7 Catalog size after each expansion step. The last bar is the "
        "committed seed used by the matching service (1163 rows)."
    )
    rep.caption(
        "Table 4.7 Runtime SQLite table medicines.",
        above=True,
    )
    rep.table(
        ["Column", "Type", "Notes"],
        [
            ["medicine_id", "String(32), PK", "MED001 … MED1163"],
            ["medicine_name", "String(255)", "Primary display and match target"],
            ["brand_name", "String(255)", "Partial and fuzzy brand matching"],
            ["active_ingredient", "String(512)", "Skipped when placeholder"],
            ["dosage", "String(128)", "May be VERIFY_FROM_OFFICIAL_LEAFLET"],
            ["form", "String(128)", "Tablet, Şurup, Kapsül, …"],
            ["category", "String(128)", "For example Ağrı Kesici"],
        ],
    )
    rep.caption(
        "Table 4.8 Runtime SQLite table scans (no user table, no foreign key to an account).",
        above=True,
    )
    rep.table(
        ["Column", "Type", "Notes"],
        [
            ["id", "Integer, PK", "Auto-increment"],
            ["created_at", "DateTime TZ", "Indexed"],
            ["detection_count, matched_count", "Integer", "Copied from analyze summary"],
            ["preview_label", "String(255)", "List UI"],
            ["filename", "String(512), nullable", "Original upload name"],
            ["ocr_mode", "String(32)", "fast / accurate"],
            ["client_device_id", "String(128), nullable", "Optional; not a login identifier"],
            ["response_json", "JSON", "Full analyze payload"],
        ],
    )
    rep.body(
        "Mobile history is a different file, scan_history.db, via sqflite, trimmed to "
        "50 rows [19]. Server history is capped at 200 rows."
    )

    rep.h2("4.10 Backend API")
    rep.body(
        "The entry point is run_api.py. The default listen address is 127.0.0.1:8000. "
        "The API prefix is /api/v1 [12], [26]. Analyze handling, in order, is: reject "
        "Content-Length above MAX_UPLOAD_SIZE_MB (default 10) before reading the body; "
        "validate extension and content-type, treating application/octet-stream as the "
        "extension MIME because Android gallery uploads use that type; check magic "
        "bytes (JPEG, PNG, WebP, BMP); optional long-edge resize to 1280 pixels; write "
        "a temporary file; run PipelineManager.analyze_all on a worker thread; delete "
        "the temporary file; attach summary, timing, image_resized, processing_time_ms "
        "and the medical disclaimer. OpenAPI documentation is served only when "
        "ENVIRONMENT is not production. The related listing is Appendix E."
    )
    rep.caption(
        "Table 4.9 REST endpoints implemented in backend/app/routers.",
        above=True,
    )
    rep.table(
        ["Method", "Path", "Purpose"],
        [
            ["GET", "/health", "status ok/degraded, models_loaded, medicine_count"],
            ["GET", "/api/v1/analyze/info", "Upload limits, OCR modes, statuses"],
            ["POST", "/api/v1/analyze", "Multipart file, query mode=fast|accurate"],
            ["GET", "/api/v1/medicines", "List/search (search, category, limit, offset)"],
            ["GET", "/api/v1/medicines/categories", "Distinct categories"],
            ["GET", "/api/v1/medicines/{id}", "Detail or 404"],
            ["GET", "/api/v1/explain/info", "LLM ready flag"],
            ["POST", "/api/v1/explain", "Short Gemini text for a matched medicine_id"],
            ["GET", "/api/v1/scans/info", "Scan-history metadata"],
            ["GET / POST", "/api/v1/scans", "List or persist analyze JSON"],
            ["GET / DELETE", "/api/v1/scans/{id}", "Detail or delete"],
        ],
    )
    rep.body(
        "Explain is a separate POST on purpose. Analyze already takes one to three "
        "minutes on CPU. The result screen loads İlaç hakkında only when the user "
        "expands the card. The primary Gemini model is gemini-flash-latest with "
        "fallback gemini-flash-lite-latest [20]. Cache key is medicine_id plus locale. "
        "Explain rate limit default is 5 requests per minute per IP. LLM_ENABLED "
        "defaults to false. The prompt is limited to catalog fields."
    )

    rep.h2("4.11 Authentication and Authorization")
    rep.body(
        "The product does not implement user signup, passwords, sessions or JWT. That "
        "is an explicit MVP limit. Calling the current design authorization would "
        "overstate it. Scan rows are not owned by a user. client_device_id is an "
        "optional string, not a verified identity."
    )
    rep.body(
        "What exists instead is as follows. Analyze, medicines, explain and scan POST "
        "or GET have no end-user login; rate limits are the main abuse control. In "
        "production, DELETE /api/v1/scans/{id} requires header X-API-Key when "
        "SCANS_API_KEY is set; if the key is unset, DELETE returns 403. Development "
        "leaves DELETE open. The Gemini key stays on the server. Placeholder strings "
        "and keys shorter than 20 characters are rejected. Android release builds use "
        "HTTPS-only network security. Debug builds allow cleartext to http://10.0.2.2 "
        "for the emulator."
    )

    rep.h2("4.12 Mobile Application")
    rep.body(
        "The Flutter module is medicine_box_app, version 0.1.0+1 [16], [17], [18]. "
        "There is no login, dashboard or admin panel. Screens that exist are splash, "
        "home with welcome / scan / history tabs, image preview with OCR mode selector "
        "and Analiz Et, result with summary chips, per-box cards, disclaimer and an "
        "expandable explanation section, and history with swipe delete. AnalyzeApiService "
        "sends a multipart POST with a 300 second timeout. Before analyze, the client "
        "calls GET /health and blocks with a SnackBar if models are not loaded. OCR mode "
        "is stored in SharedPreferences. Locale is Turkish or English."
    )
    rep.image(ASSETS / "yolocilin-logo.png", 4.4)
    rep.caption(
        "Figure 4.8 Application logo. The same asset is used as the Android launcher "
        "foreground. The application has no login screen."
    )
    rep.mono(
        "Splash -> Home\n"
        "           |- Welcome tab\n"
        "           |- Scan tab -> gallery or camera -> Preview -> health check -> Result\n"
        "           +- History tab -> saved Result\n"
        "Result -> expandable İlaç hakkında -> POST /explain"
    )
    rep.caption(
        "Figure 4.9 Mobile navigation. After a successful analyze, history save runs in "
        "the background so it does not add wait time on top of OCR. Server sync runs "
        "when the backend is reachable. CSV placeholders are rewritten in the UI instead of showing "
        "VERIFY_FROM_OFFICIAL_LEAFLET."
    )
    rep.body(
        "The emulator API URL is http://10.0.2.2:8000. Physical devices use "
        "dart-define API_BASE_URL. Gallery compression is maximum 1280 pixels at "
        "quality 65 percent."
    )

    rep.h2("4.13 Validation, Testing and Performance")
    rep.body(
        "Validation sits at four layers. Upload checks size, extension, MIME, magic "
        "bytes and empty files. Pipeline config enforces minimum OCR text length 3 and "
        "the match gates in Table 4.5. Catalog validation requires at least 900 rows, "
        "unique identifiers and a placeholder ratio below 15 percent. Production refuses "
        "CORS_ORIGINS=*. If LLM_ENABLED is true in production without a real key or "
        "mock mode, startup raises."
    )
    rep.body(
        "Backend tests run in CI on Python 3.11 [25]. Full YOLO plus EasyOCR is not "
        "executed in CI; analyze is mocked in the end-to-end smoke test because a "
        "single CPU photograph is too slow for GitHub-hosted runners. Test modules "
        "cover matching, database, API upload including octet-stream, explain, LLM "
        "configuration, scans, security (CORS, docs off, headers, HTTP 429), "
        "performance flags, model paths, CSV validation, TİTCK mapping and brand "
        "disambiguation. Flutter CI runs flutter analyze and flutter test (splash, "
        "home, result, history, JSON models, OCR-mode preferences). Live scripts "
        "scripts/e2e_api_flow.py and scripts/benchmark_analyze.py are for a local machine."
    )
    rep.caption(
        "Table 4.10 Performance numbers recorded during the internship. The 255 second "
        "figure is the first emulator baseline, not the later typical time.",
        above=True,
    )
    rep.table(
        ["Measurement", "Value"],
        [
            ["First emulator analyze (fast, CPU, one box)", "about 255 s"],
            ["Later typical fast CPU analyze", "about 1–3 minutes per photo"],
            ["A-Ferin Forte match in that first run", "about 85.7 percent, OCR text a ferin"],
            ["Mobile analyze HTTP timeout", "300 s"],
            ["E2E pytest non-OCR steps", "under 5 s each"],
            ["Medicines / scans CRUD (observed)", "under 2 s"],
            ["Docker healthcheck start-period", "180 s (EasyOCR and YOLO load)"],
            ["Analyze rate limit (default)", "20 / minute / IP"],
            ["Explain rate limit (default)", "5 / minute / IP"],
            ["Scans rate limit (default)", "30 / minute / IP"],
        ],
    )
    rep.body(
        "Performance work cut OCR search space in fast mode, added early exit, resized "
        "uploads, loaded models once, moved history I/O off the analyze wait path, and "
        "kept explain out of analyze. Accurate mode is intentionally slower. GPU remains "
        "optional (USE_GPU=true) and was not the intern default."
    )

    rep.h2("4.14 Security and DevOps")
    rep.body(
        "Implemented controls include magic-byte upload checks (the deprecated imghdr "
        "module was removed), a 10 MB cap with early Content-Length reject, per-IP rate "
        "limits, security headers (X-Content-Type-Options nosniff, X-Frame-Options DENY, "
        "Referrer-Policy strict-origin-when-cross-origin, Permissions-Policy disabling "
        "camera, microphone and geolocation on API responses), production error masking, "
        "explicit CORS in production, disabled OpenAPI docs in production, protected or "
        "disabled scan DELETE in production, gitignored secrets, and medical disclaimers. "
        "User authentication, WAF and a cloud secret manager were not implemented. The "
        "related listing is Appendix F."
    )
    rep.body(
        "Dockerfile uses python:3.12-slim-bookworm and installs libgl1, libglib2.0-0 and "
        "libgomp1 for OpenCV and EasyOCR [23]. Compose publishes port 8000, mounts "
        "weights and data/database, and caches EasyOCR models in a named volume. GitHub "
        "Actions run backend pytest, Flutter analyze and test, Docker image build, and "
        "an optional Firebase App Distribution workflow [24]. Git workflow is "
        "feature-branch, focused pull request, merge to main."
    )

    rep.h2("4.15 Problems Encountered and Solutions")
    rep.body(
        "The defects below showed up on real photographs or on the Android emulator "
        "and were then fixed in code."
    )
    p = rep._p()
    r = p.add_run("Zero YOLO boxes on blurry phone photos. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Default confidence 0.60 was too strict. Primary threshold moved to 0.40; "
        "empty or weak results retry at 0.25. Measured example: 0 boxes became 3 boxes "
        "on a blurry multi-box shot."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Short suffix OCR opened the wrong drug card. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "RapidFuzz treated three-letter pieces such as fen, alm and pal as Nurofen, "
        "Mydocalm or Gripal at WRatio ≥ 88, and fast mode stopped OCR on the first "
        "hit. The policy was tightened: suffixes are rejected, early-exit requires "
        "score ≥ 95, and a miss returns not_found (PR #67)."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Dosage OCR selected the wrong drug. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "A line such as 250 mo / j0o mo tablot scored against active_ingredient and "
        "returned Nurofen Cold and Flu for a Parafon box. Dosage-only text is now "
        "filtered, and ingredient comparison is skipped for those queries."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Euro sign instead of C on Ibucold C. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "The normalizer maps currency and copyright lookalikes to c. Adjacent OCR "
        "tokens are concatenated. Reported match after the fix: Ibucold C at score 100."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("PaddleOCR did not give better drug identity than EasyOCR. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "It was compared on the same crops and catalog. It won some boxes, produced "
        "wrong names on others, and was typically 2–4× slower on CPU. The engine was "
        "not swapped; false names came from the matcher (repository Reports 26 and 27) [33]."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Drug missing from the CSV. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Parafon was absent in the 38-row catalog. It was added, and later TİTCK "
        "expansion became the systematic answer. When a brand is still absent, "
        "token-overlap rules prefer not_found over a neighbour row. Matching cutoff "
        "was raised from 80 to 88 during the 153-row expansion (Ferrum must not match "
        "Pharmaton)."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Longer SKU names winning ties. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Parol Plus could beat Parol when OCR never saw plus. Disambiguation now uses "
        "variant tokens in the OCR evidence and prefers the base SKU when those tokens "
        "are missing."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Android HTTP 415 Unsupported Media Type. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Gallery uploads arrived as application/octet-stream. The backend now maps that "
        "MIME through the file extension; the client also sets MIME from the suffix."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Analyze felt broken because it took several minutes. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Timeout was raised to 300 seconds, loading copy was changed, gallery and "
        "server resize were added, and fast-mode OCR search space was cut. Baseline "
        "about 255 seconds; later typical fast CPU times on a clear single box range "
        "from tens of seconds to 1–3 minutes. The wait is EasyOCR on CPU; GPU was not "
        "the intern default. A retake prompt on a blurry or distant shot is expected."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Placeholder strings leaking into the UI. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "The display helper rewrites VERIFY_FROM_OFFICIAL_LEAFLET to a human sentence."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Off-by-one box labels. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "The API already used a 1-based box_index. The UI had added one again. The extra "
        "increment was removed."
    )
    set_run_font(r2)
    p = rep._p()
    r = p.add_run("Production-shaped holes. ")
    set_run_font(r, bold=True)
    r2 = p.add_run(
        "Wildcard CORS, public /docs, stack traces on 500, unlimited analyze POSTs, "
        "and cleartext in release builds were closed with environment-driven settings "
        "and tests/test_security.py. Scan DELETE in production was still too open until "
        "SCANS_API_KEY was added. Streamlit was abandoned for Flutter. Cold Docker "
        "start failed the default healthcheck window until start-period was set to 180 seconds."
    )
    set_run_font(r2)

    rep.caption(
        "Table 4.11 Numerical summary of what was delivered.",
        above=True,
    )
    rep.table(
        ["Quantity", "Value"],
        [
            ["Catalog size", "1163 medicines"],
            ["TİTCK SKRS active rows used as reference", "7948 (manifest 06.08.2026)"],
            ["Public YOLO images", "395"],
            ["YOLO class count", "1 (medicine-box)"],
            ["Final match cutoff", "88 (early-exit ≥ 95)"],
            ["Upload cap", "10 MB"],
            ["Local history cap", "50"],
            ["Server history cap", "200"],
            ["Backend pytest modules", "14 under tests/"],
            ["Flutter test files", "10 under mobile/test/"],
        ],
    )

    rep.h2("4.16 Documentation and Publication")
    rep.body(
        "The product name is Yolocilin. The GitHub repository, the GitHub Projects "
        "board, the Android application and the Kaggle dataset use the same name "
        "[5], [33]. Work was tracked with issues and pull requests. Living technical "
        "records in the repository include the EasyOCR decision (Report 26) and "
        "matching reliability (Report 27) [33]."
    )
    rep.body(
        "Training images are not committed to Git. The privacy-cleaned YOLO set of 395 "
        "images was published on Kaggle as Yolocilin Medicine Box Detection under "
        "CC BY 4.0 [5]."
    )
    rep.body(
        "During the internship, technical notes were kept in three Medium series that "
        "follow the product layers: Computer Vision (YOLOv8, OpenCV, OCR) [30], "
        "Learning REST APIs with FastAPI [31] and Database (CSV, SQLite, catalog) [32]. "
        "Those notes do not replace the product; they are a public record of methods "
        "learned on the job. Remaining titles in the same series can continue after "
        "the report is submitted."
    )

    # 5. CONCLUSION
    rep.h1("5. CONCLUSION")
    rep.body(
        "The internship left a working product: a trained single-class detector, an OCR "
        "and matching pipeline with explicit failure statuses, a FastAPI service, a "
        "1163-row TİTCK-enriched catalog, an Android client, Docker packaging and CI. "
        "Work ran in feature branches against GitHub issues. The dataset is on Kaggle; "
        "the technical notes are in the Medium series.",
        first=True,
    )
    rep.body(
        "The technically useful lesson was that detection accuracy on clean Roboflow "
        "images is not the same problem as identification on a kitchen-table photograph. "
        "Most of the engineering time after the first best.pt went into OCR variants, "
        "RapidFuzz guards, catalog quality, and making a three-minute CPU call usable "
        "in a mobile UI. Raising the match cutoff and refusing foreign brand tokens "
        "and suffix OCR fragments mattered more for trust than adding another YOLO "
        "scale or OCR engine. After the first false matches, the goal was that the "
        "system should fail as not_found more often than as the wrong brand."
    )
    rep.body(
        "Limits are part of the result. There is no user authentication; server scan "
        "history is global. Inference is CPU-bound and far from real-time; blurry or "
        "distant photos make OCR slow or return not_found. The catalog is not the full "
        "TİTCK list. iOS, PostgreSQL, barcode reading and a public HTTPS deployment "
        "were left as later items. Gemini explanations are optional and must not be "
        "read as a prospectus."
    )
    rep.body(
        "For a computer engineering internship the delivery is a working vertical slice: "
        "vision model, data pipeline, HTTP API, mobile client, tests, and the operational "
        "files needed to run the system on another machine. As required by the department "
        "booklet, each inner page should carry the student signature at the bottom left "
        "and the responsible engineer’s signature and company stamp at the bottom right."
    )

    # APPENDIXES
    rep.h1("APPENDIXES")
    rep.body(
        "Internship writing rules require that code appear only in this section, not in "
        "the body. The listings are shortened excerpts from the relevant functions, not "
        "complete files. The full source is in the Yolocilin GitHub repository [33]. A "
        "separate code report, or copying every file into Word, is not required. Line "
        "spacing in this section is single.",
        first=True,
    )
    rep.caption(
        "Table APX.1 Source files for the appendix excerpts. Full code is in [33].",
        above=True,
    )
    rep.table(
        ["Appendix", "File", "What is shown"],
        [
            ["A", "src/preprocessing/color_operations.py, src/ocr/ocr_pipeline.py", "CLAHE and sharpening"],
            ["B", "src/services/detection_service.py", "YOLO confidence fallback"],
            ["C", "src/ocr/ocr_pipeline.py, src/services/config.py", "Fast OCR variants"],
            ["D", "src/matching/medicine_matcher.py", "RapidFuzz matching"],
            ["E", "backend/app/services/analyze_service.py", "Upload and resize"],
            ["F", "backend/app/middleware/security_headers.py", "Security headers"],
            ["G", "data/samples/", "Sample photographs are in Section 4"],
        ],
    )

    rep.h2("Appendix A  OpenCV Preprocessing (CLAHE and sharpening)")
    rep.body(
        "Source: src/preprocessing/color_operations.py and src/ocr/ocr_pipeline.py. "
        "CLAHE raises local contrast; the sharpening kernel makes print edges clearer. "
        "These two operations are the basis of the variants generated before OCR [9]."
    )
    rep.code(
        "def convert_to_grayscale(image):\n"
        "    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)\n"
        "\n"
        "def apply_clahe(grayscale_image, clip_limit=2.0, tile_grid_size=(8, 8)):\n"
        "    clahe = cv2.createCLAHE(\n"
        "        clipLimit=clip_limit,\n"
        "        tileGridSize=tile_grid_size,\n"
        "    )\n"
        "    return clahe.apply(grayscale_image)\n"
        "\n"
        "def apply_sharpening(image):\n"
        "    kernel = np.array(\n"
        "        [[0, -1, 0], [-1, 5, -1], [0, -1, 0]],\n"
        "        dtype=np.float32,\n"
        "    )\n"
        "    return cv2.filter2D(image, ddepth=-1, kernel=kernel)"
    )

    rep.h2("Appendix B  YOLO Confidence Fallback")
    rep.body(
        "Source: src/services/detection_service.py (detect_all). Primary threshold 0.40. "
        "If there are no boxes, or the best score is below 0.55 and a 0.25 pass finds "
        "more boxes, the fallback result is kept."
    )
    rep.code(
        "primary_threshold = self.config.confidence_threshold          # 0.40\n"
        "fallback_threshold = self.config.fallback_confidence_threshold  # 0.25\n"
        "detected_boxes = self._detect_at_threshold(image_path, primary_threshold)\n"
        "should_use_fallback = not detected_boxes\n"
        "if detected_boxes and max(box.confidence for box in detected_boxes) < 0.55:\n"
        "    fallback_boxes = self._detect_at_threshold(image_path, fallback_threshold)\n"
        "    if len(fallback_boxes) > len(detected_boxes):\n"
        "        detected_boxes = fallback_boxes\n"
        "        should_use_fallback = True\n"
        "if not detected_boxes:\n"
        "    detected_boxes = self._detect_at_threshold(image_path, fallback_threshold)"
    )

    rep.h2("Appendix C  Fast-Mode OCR Variants")
    rep.body(
        "Source: src/ocr/ocr_pipeline.py (add_minimal_variants) and src/services/config.py. "
        "Fast mode keeps original plus sharpened per rotation and may stop early."
    )
    rep.code(
        "def add_minimal_variants(variants, prefix, image) -> None:\n"
        '    """Fast OCR mode: 2 variants per angle."""\n'
        '    variants[f"{prefix}_original_color"] = image\n'
        '    variants[f"{prefix}_sharpened_color"] = apply_sharpening(image)\n'
        "\n"
        "# PipelineConfig (excerpt)\n"
        "confidence_threshold: float = 0.40\n"
        "fallback_confidence_threshold: float = 0.25\n"
        "ocr_scale_factor_fast: float = 1.75\n"
        "max_image_dimension: int = 1280\n"
        "minimum_match_score: float = 88.0\n"
        "minimum_partial_match_text_length: int = 5\n"
        "early_exit_minimum_score: float = 95.0\n"
        'ocr_languages: tuple[str, ...] = ("tr", "en")\n'
        'ocr_mode: OCRMode = "fast"\n'
        "# ocr_rotation_angles -> (0, 90, 180, 270)\n"
        "# ocr_early_exit -> True when ocr_mode == fast"
    )

    rep.h2("Appendix D  RapidFuzz Matching")
    rep.body(
        "Source: src/matching/medicine_matcher.py and src/matching/text_normalizer.py. "
        "Similarity is fuzz.WRatio after normalize_ocr_text [11]."
    )
    rep.code(
        "def calculate_text_similarity(query_text: str, medicine_name: str) -> float:\n"
        "    cleaned_query = normalize_text(query_text)\n"
        "    cleaned_medicine_name = normalize_text(medicine_name)\n"
        "    if not cleaned_query or not cleaned_medicine_name:\n"
        "        return 0.0\n"
        "    return float(fuzz.WRatio(cleaned_query, cleaned_medicine_name))\n"
        "\n"
        "OCR_CONFUSABLE_TRANSLATION = str.maketrans(\n"
        '    {"€": "c", "©": "c", "¢": "c"}\n'
        ")"
    )

    rep.h2("Appendix E  Analyze Upload Path")
    rep.body(
        "Source: backend/app/services/analyze_service.py. Validation and resize happen "
        "before asyncio.to_thread."
    )
    rep.code(
        "suffix = validate_upload_metadata(\n"
        "    filename=filename,\n"
        "    content_type=content_type,\n"
        "    allowed_extensions=self.settings.allowed_extensions,\n"
        ")\n"
        "validate_image_bytes(file_bytes, suffix=suffix)\n"
        "file_bytes, resized = resize_image_bytes_if_large(\n"
        "    file_bytes,\n"
        "    max_dimension=self.manager.config.max_image_dimension,\n"
        "    suffix=suffix,\n"
        ")\n"
        "result = await asyncio.to_thread(\n"
        "    _run_analysis, self.manager, temp_path, ocr_mode=selected_mode,\n"
        ")"
    )

    rep.h2("Appendix F  Security Headers")
    rep.body("Source: backend/app/middleware/security_headers.py.")
    rep.code(
        'response.headers.setdefault("X-Content-Type-Options", "nosniff")\n'
        'response.headers.setdefault("X-Frame-Options", "DENY")\n'
        'response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")\n'
        "response.headers.setdefault(\n"
        '    "Permissions-Policy", "camera=(), microphone=(), geolocation=()",\n'
        ")"
    )

    rep.h2("Appendix G  Sample Photographs")
    rep.body(
        "Clearer package photographs used in the report are placed in Section 4 "
        "(Figures 4.4 to 4.6) so that they sit next to the detection and OCR discussion. "
        "Blurry handheld shots and photos that include unrelated household objects were "
        "left out of the printed figures."
    )

    # RESOURCES
    rep.h1("RESOURCES")
    refs = [
        '[1] Cerebrum Technologies, “Cerebrum Technologies” (homepage: mission, AI description, Ankara office address), accessed 13 August 2026. https://www.cerebrumtechnologies.com',
        '[2] Cerebrum Tech, “Hakkımızda / About” (mission text; message from R. Erdem Erkul, PhD), accessed 13 August 2026. https://www.cerebrumtechnologies.com/en/hakkımızda',
        '[3] Cerebrum Tech, “Sürdürülebilirlik” (forest fire detection; beekeeping and smart agriculture), accessed 13 August 2026. https://www.cerebrumtechnologies.com/en/copy-of-vizyonumuz',
        '[4] Cerebrum Tech, “Ekibimiz” (founders and management titles as published), accessed 13 August 2026. https://www.cerebrumtechnologies.com/en/ekibimiz-ile-tanisin',
        '[5] Kaggle, “Yolocilin Medicine Box Detection” (dataset slug melikeklahc/yolocilin-medicine-box-detection), CC BY 4.0, accessed 13 August 2026. https://www.kaggle.com/datasets/melikeklahc/yolocilin-medicine-box-detection',
        '[6] Ultralytics, YOLOv8 Docs, accessed 13 August 2026. https://docs.ultralytics.com',
        '[7] Jocher, G., Chaurasia, A., Qiu, J., Ultralytics YOLO, 2023. https://github.com/ultralytics/ultralytics',
        '[8] Redmon, J., Divvala, S., Girshick, R., Farhadi, A., “You Only Look Once: Unified, Real-Time Object Detection,” Proc. IEEE Conference on Computer Vision and Pattern Recognition, 2016, pp. 779–788.',
        '[9] OpenCV, OpenCV Documentation, accessed 13 August 2026. https://docs.opencv.org',
        '[10] JaidedAI, EasyOCR, accessed 13 August 2026. https://github.com/JaidedAI/EasyOCR',
        '[11] RapidFuzz, RapidFuzz Documentation (fuzz.WRatio), accessed 13 August 2026. https://rapidfuzz.github.io/RapidFuzz',
        '[12] FastAPI, FastAPI Documentation, accessed 13 August 2026. https://fastapi.tiangolo.com',
        '[13] Pydantic, Pydantic Documentation, accessed 13 August 2026. https://docs.pydantic.dev',
        '[14] SQLAlchemy, SQLAlchemy 2.0 Documentation, accessed 13 August 2026. https://docs.sqlalchemy.org',
        '[15] SQLite, SQLite Documentation, accessed 13 August 2026. https://www.sqlite.org/docs.html',
        '[16] Flutter, Flutter Documentation, accessed 13 August 2026. https://docs.flutter.dev',
        '[17] Dart, http package, accessed 13 August 2026. https://pub.dev/packages/http',
        '[18] Flutter, image_picker package, accessed 13 August 2026. https://pub.dev/packages/image_picker',
        '[19] Flutter, sqflite package, accessed 13 August 2026. https://pub.dev/packages/sqflite',
        '[20] Google, Gemini API / Google GenAI Python SDK, accessed 13 August 2026. https://ai.google.dev',
        '[21] T.C. Sağlık Bakanlığı, Türkiye İlaç ve Tıbbi Cihaz Kurumu (TİTCK), “SKRS E-Reçete İlaç ve Diğer Farmasötik Ürünler Listesi,” accessed 13 August 2026. https://www.titck.gov.tr/dinamikmodul/43',
        '[22] Roboflow, Roboflow Documentation, accessed 13 August 2026. https://docs.roboflow.com',
        '[23] Docker, Docker Documentation, accessed 13 August 2026. https://docs.docker.com',
        '[24] GitHub, GitHub Actions Documentation, accessed 13 August 2026. https://docs.github.com/en/actions',
        '[25] pytest, pytest Documentation, accessed 13 August 2026. https://docs.pytest.org',
        '[26] Uvicorn, Uvicorn Documentation, accessed 13 August 2026. https://www.uvicorn.org',
        '[27] Creative Commons, Attribution 4.0 International (CC BY 4.0), accessed 13 August 2026. https://creativecommons.org/licenses/by/4.0/',
        '[28] PyTorch, PyTorch Documentation, accessed 13 August 2026. https://pytorch.org/docs/stable/index.html',
        '[29] Düzce University Faculty of Engineering, Computer Engineering Department, Internship Report Preparation Booklet (StajRaporuİngilizce), n.d.',
        '[30] Külahcı, M. E., “Computer Vision” (Medium series; Yolocilin vision, OpenCV and OCR notes), accessed 13 August 2026. https://medium.com/@m.edakulahci/list/computer-vision-d0f63fcdf7d2',
        '[31] Külahcı, M. E., “Learning REST APIs with FastAPI” (Medium series; Yolocilin backend notes), accessed 13 August 2026. https://medium.com/@m.edakulahci/list/learning-rest-apis-with-fastapi-ad9c2442f9d6',
        '[32] Külahcı, M. E., “Database” (Medium series; CSV, SQLite and catalog notes), accessed 13 August 2026. https://medium.com/@m.edakulahci/list/database-25184640519a',
        '[33] Külahcı, M. E., Yolocilin (GitHub repository), accessed 13 August 2026. https://github.com/Melikeda/yolocilin',
    ]
    for item in refs:
        p = rep._p(align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing=1.0, indent=False, space_before=0, space_after=6)
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        r = p.add_run(item)
        set_run_font(r, size=12)

    for section in doc.sections:
        set_page_border(section)

    OUT_DOCS.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_DOCS))
    try:
        OUT_DOWNLOADS.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(OUT_DOWNLOADS))
    except OSError:
        pass
    print(f"Wrote {OUT_DOCS}")
    if OUT_DOWNLOADS.exists():
        print(f"Wrote {OUT_DOWNLOADS}")


if __name__ == "__main__":
    build()
