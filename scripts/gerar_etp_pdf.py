#!/usr/bin/env python3
"""Gera o PDF do ETP a partir do conteúdo Markdown versionado no repositório."""

from pathlib import Path
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "ETP_qualidade_agua_modbus.md"
OUTPUT = ROOT / "docs" / "ETP_qualidade_agua_modbus.pdf"


def inline_markup(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


class HorizontalRule(Flowable):
    def __init__(self, width: float):
        super().__init__()
        self.width = width
        self.height = 5 * mm

    def draw(self):
        self.canv.setStrokeColor(colors.HexColor("#9aa6a0"))
        self.canv.line(0, self.height / 2, self.width, self.height / 2)


def parse_markdown(path: Path, styles):
    lines = path.read_text(encoding="utf-8").splitlines()
    story = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                current = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(set(cell) <= set("-: ") for cell in current):
                    rows.append([Paragraph(inline_markup(cell), styles["ETPTableCell"]) for cell in current])
                index += 1
            if rows:
                table = Table(rows, repeatRows=1)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dce8e2")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#173b32")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#aab8b0")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.extend([table, Spacer(1, 5 * mm)])
            continue
        match = re.match(r"^(#{1,3})\s+(.*)$", line)
        if match:
            level = len(match.group(1))
            style = styles["ETPTitle"] if level == 1 else styles[f"ETPHeading{level}"]
            story.append(Paragraph(inline_markup(match.group(2)), style))
            index += 1
            continue
        if line.startswith(">"):
            story.append(Paragraph(inline_markup(line[1:].strip()), styles["ETPNote"]))
            index += 1
            continue
        if re.match(r"^(?:- |\d+\. )", line):
            item = re.sub(r"^(?:- |\d+\. )", "", line)
            story.append(Paragraph("• " + inline_markup(item), styles["ETPBullet"]))
            index += 1
            continue
        story.append(Paragraph(inline_markup(line), styles["ETPBodyText"]))
        index += 1
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#c7d0cb"))
    canvas.line(18 * mm, 14 * mm, 192 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#66736d"))
    canvas.drawString(18 * mm, 9 * mm, "ETP - Aquisição de dados de qualidade da água")
    canvas.drawRightString(192 * mm, 9 * mm, f"Página {doc.page}")
    canvas.restoreState()


def main() -> int:
    if not SOURCE.exists():
        print(f"Arquivo de origem não encontrado: {SOURCE}", file=sys.stderr)
        return 1
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ETPTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#173b32"), alignment=TA_CENTER, spaceAfter=8 * mm))
    styles.add(ParagraphStyle(name="ETPHeading2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#1e5a4b"), spaceBefore=5 * mm, spaceAfter=2 * mm, keepWithNext=True))
    styles.add(ParagraphStyle(name="ETPHeading3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#34584e"), spaceBefore=3 * mm, spaceAfter=1.5 * mm, keepWithNext=True))
    styles.add(ParagraphStyle(name="ETPBodyText", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, alignment=TA_LEFT, spaceAfter=2.5 * mm))
    styles.add(ParagraphStyle(name="ETPBullet", parent=styles["BodyText"], leftIndent=7 * mm, firstLineIndent=-4 * mm, spaceAfter=1.2 * mm))
    styles.add(ParagraphStyle(name="ETPNote", parent=styles["BodyText"], backColor=colors.HexColor("#edf3ef"), borderColor=colors.HexColor("#9ab4a7"), borderWidth=0.5, borderPadding=6, spaceBefore=2 * mm, spaceAfter=4 * mm))
    styles.add(ParagraphStyle(name="ETPTableCell", parent=styles["BodyText"], fontSize=7.5, leading=9.5, spaceAfter=0))
    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=17 * mm, bottomMargin=19 * mm, title="Estudo Técnico Preliminar - Qualidade da Água")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])
    story = parse_markdown(SOURCE, styles)
    story.insert(2, HorizontalRule(doc.width))
    doc.build(story)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())