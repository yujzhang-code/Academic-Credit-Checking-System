# pdf_generator.py — PDF 產生函數

import os
from io import BytesIO
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from translations import zh, en


def register_font():
    candidates = [
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msjhbd.ttc",
        "C:/Windows/Fonts/mingliu.ttc",
        "C:/Windows/Fonts/kaiu.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("CJKFont", path))
                return "CJKFont"
            except Exception:
                continue
    return "Helvetica"


CJK_FONT = register_font()


def _styles():
    base = getSampleStyleSheet()
    font = CJK_FONT
    make = lambda name, size, color=colors.black, space_before=0: ParagraphStyle(
        name, parent=base["Normal"],
        fontName=font, fontSize=size, leading=size * 1.6,
        textColor=color, spaceBefore=space_before,
    )
    return {
        "title":  make("T", 15, colors.HexColor("#1a3a5c")),
        "sub":    make("S", 9,  colors.HexColor("#555555")),
        "h2":     make("H", 11, colors.HexColor("#1a3a5c"), space_before=8),
        "normal": make("N", 9),
        "small":  make("Sm", 7.5, colors.HexColor("#666666")),
        "red":    make("R", 9,  colors.HexColor("#cc0000")),
        "green":  make("G", 9,  colors.HexColor("#007a33")),
        "en":     make("En", 8, colors.HexColor("#444444")),
    }


def _header(story, sid, qt, qt_en, qualified, s):
    story.append(Paragraph(zh("dept_name"), s["sub"]))
    story.append(Paragraph(en("dept_name"), s["sub"]))
    story.append(Spacer(1, 3))
    story.append(Paragraph(zh("pdf_title"), s["title"]))
    story.append(Paragraph(en("pdf_title"), s["sub"]))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=colors.HexColor("#1a3a5c")))
    story.append(Spacer(1, 6))

    result_zh = zh("pdf_pass") if qualified else zh("pdf_fail")
    result_en = en("pdf_pass") if qualified else en("pdf_fail")
    result_color = (colors.HexColor("#007a33") if qualified
                    else colors.HexColor("#cc0000"))

    data = [
        [f"{zh('pdf_sid')} / {en('pdf_sid')}", sid,
         f"{zh('pdf_date')} / {en('pdf_date')}",
         date.today().strftime("%Y-%m-%d")],
        [f"{zh('pdf_query')} / {en('pdf_query')}", f"{qt}\n{qt_en}",
         f"{zh('pdf_result')} / {en('pdf_result')}",
         f"{result_zh}\n{result_en}"],
    ]
    tbl = Table(data, colWidths=[38*mm, 52*mm, 38*mm, 42*mm])
    tbl.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (-1,-1), CJK_FONT),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#dde8f0")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#dde8f0")),
        ("BOX",        (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("PADDING",    (0,0), (-1,-1), 4),
        ("TEXTCOLOR",  (3,1), (3,1), result_color),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 8))


def _footer(story, s):
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 4))
    story.append(Paragraph(zh("system_note"), s["small"]))
    story.append(Paragraph(en("system_note"), s["small"]))


def _gaps_section(story, gaps, notes, s):
    story.append(Paragraph(
        f"{zh('pdf_gaps')}　{en('pdf_gaps')}", s["h2"]))
    if gaps:
        for g in gaps:
            story.append(Paragraph(f"• {g['zh']}", s["red"]))
            story.append(Paragraph(f"  {g['en']}", s["en"]))
    else:
        story.append(Paragraph(zh("pdf_no_gaps"), s["green"]))
        story.append(Paragraph(en("pdf_no_gaps"), s["en"]))

    if notes:
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"{zh('pdf_notes')}　{en('pdf_notes')}", s["h2"]))
        for n in notes:
            story.append(Paragraph(f"• {n['zh']}", s["normal"]))
            story.append(Paragraph(f"  {n['en']}", s["en"]))


def gen_pdf_master(sid, qt, qt_en, qualified, gaps, notes,
                   credits, eng_label_zh, eng_label_en, eng_pass):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    s = _styles()
    story = []
    _header(story, sid, qt, qt_en, qualified, s)

    story.append(Paragraph(
        f"{zh('pdf_credits')}　{en('pdf_credits')}", s["h2"]))
    rows = [
        [f"{zh('pdf_item')}\n{en('pdf_item')}",
         f"{zh('pdf_required')}\n{en('pdf_required')}",
         f"{zh('pdf_completed')}\n{en('pdf_completed')}",
         f"{zh('pdf_status')}\n{en('pdf_status')}"],
        ["642 D0100 專題討論\nSeminar",
         "4 學分\n4 credits",
         f"{credits['seminar']} 學分\n{credits['seminar']} cr.",
         "✓" if credits["seminar"] >= 4 else "✗"],
        ["生物技術核心實驗\nBiotechnology Core Techniques",
         "4 學分\n4 credits",
         "已修✓\nCompleted" if credits["core_lab_pass"] else "未修✗\nNot completed",
         "✓" if credits["core_lab_pass"] else "✗"],
        ["必選修課程（二選一）\nRequired Elective (1 of 2)",
         "2 學分\n2 credits",
         "已修✓\nCompleted" if credits["mgmt_ok"] else "未修✗\nNot completed",
         "✓" if credits["mgmt_ok"] else "✗"],
        ["本所 M/D 字頭必修\nRequired M/D courses",
         "6 學分\n6 credits",
         f"{credits['dept_req']} 學分\n{credits['dept_req']} cr.",
         "✓" if credits["dept_req"] >= 6 else "✗"],
        ["選修\nElectives",
         "10 學分\n10 credits",
         f"{credits['elective']} 學分\n{credits['elective']} cr.",
         "✓" if credits["elective"] >= 10 else "✗"],
        ["合計\nTotal",
         "24 學分\n24 credits",
         f"{credits['total']} 學分\n{credits['total']} cr.",
         "✓" if credits["total"] >= 24 else "✗"],
        ["642 M0010 碩士論文\nDissertation (M)",
         "當學期選修\nEnroll this semester",
         "已選✓\nEnrolled" if credits["thesis_enrolled"] else "未選✗\nNot enrolled",
         "✓" if credits["thesis_enrolled"] else "✗"],
    ]
    ct = Table(rows, colWidths=[55*mm, 28*mm, 28*mm, 14*mm])
    ct.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-1), CJK_FONT),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1a3a5c")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f2f7fb")]),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("PADDING",       (0,0), (-1,-1), 4),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        f"{zh('pdf_english')}　{en('pdf_english')}", s["h2"]))
    eng_status_zh = zh("eng_pass_label") if eng_pass else zh("eng_fail_label")
    eng_status_en = en("eng_pass_label") if eng_pass else en("eng_fail_label")
    eng_style = s["green"] if eng_pass else s["red"]
    story.append(Paragraph(f"{eng_status_zh} — {eng_label_zh}", eng_style))
    story.append(Paragraph(f"{eng_status_en} — {eng_label_en}", s["en"]))
    story.append(Spacer(1, 8))

    _gaps_section(story, gaps, notes, s)
    _footer(story, s)
    doc.build(story)
    return buf.getvalue()


def gen_pdf_phd(sid, qt, qt_en, qualified, gaps, notes,
                credits, eng_label_zh, eng_label_en, eng_pass):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    s = _styles()
    story = []
    _header(story, sid, qt, qt_en, qualified, s)

    story.append(Paragraph(
        f"{zh('pdf_credits')}　{en('pdf_credits')}", s["h2"]))
    rows = [
        [f"{zh('pdf_item')}\n{en('pdf_item')}",
         f"{zh('pdf_required')}\n{en('pdf_required')}",
         f"{zh('pdf_completed')}\n{en('pdf_completed')}",
         f"{zh('pdf_status')}\n{en('pdf_status')}"],
        ["高等生物科技特論（一）\nSelected Topics in Advanced Biotech (I)",
         "3 學分\n3 credits",
         "已修✓\nCompleted" if credits["adv1"] else "未修✗\nNot completed",
         "✓" if credits["adv1"] else "✗"],
        ["高等生物科技特論（二）\nSelected Topics in Advanced Biotech (II)",
         "3 學分\n3 credits",
         "已修✓\nCompleted" if credits["adv2"] else "未修✗\nNot completed",
         "✓" if credits["adv2"] else "✗"],
        ["本所必選課程（9選2）\nRequired Electives (2 of 9)",
         "6 學分\n6 credits",
         f"{credits['chosen']} 學分\n{credits['chosen']} cr.",
         "✓" if credits["chosen"] >= 6 else "✗"],
        ["選修\nElectives",
         "4 學分\n4 credits",
         f"{credits['elective']} 學分\n{credits['elective']} cr.",
         "✓" if credits["elective"] >= 4 else "✗"],
        ["合計\nTotal",
         "20 學分\n20 credits",
         f"{credits['total']} 學分\n{credits['total']} cr.",
         "✓" if credits["total"] >= 20 else "✗"],
    ]
    ct = Table(rows, colWidths=[65*mm, 25*mm, 25*mm, 14*mm])
    ct.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-1), CJK_FONT),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#1a3a5c")),
        ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.white, colors.HexColor("#f2f7fb")]),
        ("BOX",           (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("PADDING",       (0,0), (-1,-1), 4),
        ("ALIGN",         (1,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(ct)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        f"{zh('pdf_english')}　{en('pdf_english')}", s["h2"]))
    eng_status_zh = zh("eng_pass_label") if eng_pass else zh("eng_fail_label")
    eng_status_en = en("eng_pass_label") if eng_pass else en("eng_fail_label")
    eng_style = s["green"] if eng_pass else s["red"]
    story.append(Paragraph(f"{eng_status_zh} — {eng_label_zh}", eng_style))
    story.append(Paragraph(f"{eng_status_en} — {eng_label_en}", s["en"]))
    story.append(Spacer(1, 8))

    _gaps_section(story, gaps, notes, s)
    _footer(story, s)
    doc.build(story)
    return buf.getvalue()
