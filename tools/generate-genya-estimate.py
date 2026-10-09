from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
PDF_PATH = OUTPUT / "立ち食い寿司_ゲンヤ倶楽部_SAKURA_Site_Controller_正式見積書_20261009.pdf"
FONT_PATH = Path(r"C:\Windows\Fonts\NotoSansJP-VF.ttf")

BLUE = colors.HexColor("#0075de")
PINK = colors.HexColor("#e91e63")
INK = colors.HexColor("#252321")
MUTED = colors.HexColor("#615d59")
LINE = colors.HexColor("#d9d6d2")
WARM = colors.HexColor("#f6f5f4")
PALE_BLUE = colors.HexColor("#eef6fc")
GREEN = colors.HexColor("#238636")


def register_font() -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Japanese font not found: {FONT_PATH}")
    pdfmetrics.registerFont(TTFont("NotoSansJP", str(FONT_PATH)))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="NotoSansJP", fontSize=23, leading=31, textColor=INK, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", parent=base["BodyText"], fontName="NotoSansJP", fontSize=10, leading=16, textColor=MUTED, alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="NotoSansJP", fontSize=15, leading=22, textColor=INK, spaceBefore=3 * mm, spaceAfter=3 * mm, keepWithNext=True),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="NotoSansJP", fontSize=11, leading=17, textColor=BLUE, spaceBefore=3 * mm, spaceAfter=2 * mm, keepWithNext=True),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontName="NotoSansJP", fontSize=8.8, leading=14.5, textColor=INK, spaceAfter=2 * mm, wordWrap="CJK"),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontName="NotoSansJP", fontSize=7.5, leading=12, textColor=MUTED, wordWrap="CJK"),
        "table_head": ParagraphStyle("table_head", parent=base["BodyText"], fontName="NotoSansJP", fontSize=7.8, leading=12, textColor=colors.white, alignment=TA_CENTER, wordWrap="CJK"),
        "table_text": ParagraphStyle("table_text", parent=base["BodyText"], fontName="NotoSansJP", fontSize=7.8, leading=12, textColor=INK, wordWrap="CJK"),
        "table_num": ParagraphStyle("table_num", parent=base["BodyText"], fontName="NotoSansJP", fontSize=7.8, leading=12, textColor=INK, alignment=TA_RIGHT),
        "amount": ParagraphStyle("amount", parent=base["BodyText"], fontName="NotoSansJP", fontSize=15, leading=22, textColor=BLUE, alignment=TA_RIGHT),
    }


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
    canvas.setFont("NotoSansJP", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8.5 * mm, "株式会社さくらねっと / SAKURA Site Controller")
    canvas.drawRightString(A4[0] - 18 * mm, 8.5 * mm, f"SKN-EST-20261009-01 / {doc.page}")
    canvas.restoreState()


def money(value: int) -> str:
    return f"¥{value:,}"


def line_item_table(items, st, total_label):
    data = [[
        Paragraph("品目", st["table_head"]),
        Paragraph("数量", st["table_head"]),
        Paragraph("単価（税別）", st["table_head"]),
        Paragraph("金額（税別）", st["table_head"]),
    ]]
    subtotal = 0
    for name, qty, unit, price in items:
        amount = qty * price
        subtotal += amount
        data.append([
            Paragraph(name, st["table_text"]),
            Paragraph(f"{qty}{unit}", st["table_num"]),
            Paragraph(money(price), st["table_num"]),
            Paragraph(money(amount), st["table_num"]),
        ])
    tax = subtotal // 10
    data.extend([
        [Paragraph(f"{total_label}小計", st["table_text"]), "", "", Paragraph(money(subtotal), st["table_num"])],
        [Paragraph("消費税（10%）", st["table_text"]), "", "", Paragraph(money(tax), st["table_num"])],
        [Paragraph(f"{total_label}合計", st["table_text"]), "", "", Paragraph(money(subtotal + tax), st["table_num"])],
    ])
    table = Table(data, colWidths=[91 * mm, 18 * mm, 28 * mm, 29 * mm], repeatRows=1)
    last = len(data) - 1
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("SPAN", (0, last - 2), (2, last - 2)),
        ("SPAN", (0, last - 1), (2, last - 1)),
        ("SPAN", (0, last), (2, last)),
        ("BACKGROUND", (0, last - 2), (-1, last - 1), WARM),
        ("BACKGROUND", (0, last), (-1, last), PALE_BLUE),
        ("TEXTCOLOR", (0, last), (-1, last), BLUE),
        ("LINEABOVE", (0, last), (-1, last), 1.2, BLUE),
    ]))
    return table, subtotal + tax


def callout(text, st, edge=BLUE, background=PALE_BLUE):
    table = Table([[Paragraph(text, st["body"])]], colWidths=[166 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), background),
        ("BOX", (0, 0), (-1, -1), 0.5, edge),
        ("LINEBEFORE", (0, 0), (0, -1), 3, edge),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def bullet(text, st):
    style = ParagraphStyle("bullet_item", parent=st["body"], leftIndent=5 * mm, firstLineIndent=-4 * mm, spaceAfter=1.3 * mm)
    return Paragraph(f"• {text}", style)


def build_pdf() -> None:
    register_font()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    st = styles()
    doc = BaseDocTemplate(
        str(PDF_PATH), pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="SAKURA Site Controller 予約統合システム 正式見積書",
        author="株式会社さくらねっと",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=footer)])

    initial_items = [
        ("SAKURA Site Controller 基本導入・初期設定", 1, "式", 70000),
        ("HP予約・食べログ通知・Gmail・Google Calendar連携設定", 1, "式", 40000),
        ("SAKURA BLOOM・Notion・監視通知設定", 1, "式", 20000),
        ("操作マニュアル・初期説明・受入確認", 1, "式", 20000),
    ]
    monthly_items = [
        ("システム利用・自動連携・稼働監視", 1, "店舗", 10000),
        ("保守・障害一次対応・遠隔サポート", 1, "店舗", 5000),
    ]
    initial_table, initial_total = line_item_table(initial_items, st, "初期費用")
    monthly_table, monthly_total = line_item_table(monthly_items, st, "月額")

    issuer = Table([
        [Paragraph("発行日", st["small"]), Paragraph("2026年10月9日", st["body"])],
        [Paragraph("見積番号", st["small"]), Paragraph("SKN-EST-20261009-01", st["body"])],
        [Paragraph("有効期限", st["small"]), Paragraph("2026年11月8日", st["body"])],
    ], colWidths=[25 * mm, 45 * mm])
    issuer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))

    story = [
        Table([[""]], colWidths=[28 * mm], rowHeights=[2.5 * mm], style=[("BACKGROUND", (0, 0), (-1, -1), PINK)]),
        Spacer(1, 5 * mm),
        Paragraph("見　積　書", st["title"]),
        Paragraph("SAKURA Site Controller 予約統合システム", st["subtitle"]),
        Spacer(1, 6 * mm),
        Table([
            [Paragraph("立ち食い寿司 ゲンヤ倶楽部　御中", st["h1"]), issuer],
            [Paragraph("下記のとおりお見積り申し上げます。", st["body"]), Paragraph("〒532-0012<br/>大阪市淀川区木川東4-3-34-514<br/><b>株式会社さくらねっと</b><br/>TEL 06-7777-2720　FAX 06-6303-3767<br/>担当者：伏見", st["small"])],
        ], colWidths=[92 * mm, 74 * mm], style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (0, 0), 1, INK), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]),
        Spacer(1, 6 * mm),
        Table([
            [Paragraph("初期費用（税込）", st["body"]), Paragraph(money(initial_total), st["amount"])],
            [Paragraph("月額利用料（税込）", st["body"]), Paragraph(money(monthly_total), st["amount"])],
        ], colWidths=[82 * mm, 84 * mm], style=[("BACKGROUND", (0, 0), (-1, -1), WARM), ("BOX", (0, 0), (-1, -1), 0.7, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]),
        Spacer(1, 5 * mm),
        Paragraph("初期導入費", st["h2"]),
        initial_table,
        Spacer(1, 4 * mm),
        Paragraph("月額利用料", st["h2"]),
        monthly_table,
        Spacer(1, 4 * mm),
        callout("初回請求は初期費用165,000円（税込）です。月額利用料16,500円（税込）は本稼働開始月から発生します。機器代は含まれていません。", st),
        Spacer(1, 5 * mm),
        Paragraph("提供範囲・条件", st["h1"]),
        Table([
            [Paragraph("本見積に含まれる内容", st["table_head"]), Paragraph("本見積に含まれない内容", st["table_head"])],
            [Paragraph("• ホームページ予約受付と管理画面<br/>• 食べログ等の予約通知メール取込<br/>• Gmail・Google Calendar・Notion・SAKURA BLOOM連携<br/>• 予約確定、日時変更、キャンセル、参加人数管理<br/>• 障害・復旧メール通知と定期監視<br/>• 操作・技術運用マニュアル<br/>• 月30分の遠隔支援、月1回の軽微設定変更", st["table_text"]),
             Paragraph("• iPad、PC、スタンド等の機器代<br/>• 回線、モバイル通信、店内ネットワーク工事<br/>• Google Workspace、食べログ等の第三者契約料<br/>• Google公式予約API等の新規直接接続<br/>• 新機能開発、大規模改修、データ移行、現地訪問<br/>• 24時間365日の有人対応、緊急駆け付け", st["table_text"])],
        ], colWidths=[83 * mm, 83 * mm], style=[
            ("BACKGROUND", (0, 0), (-1, 0), BLUE), ("GRID", (0, 0), (-1, -1), 0.45, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]),
        Spacer(1, 4 * mm),
        Paragraph("見積条件", st["h2"]),
        Table([
            [Paragraph("対象", st["small"]), Paragraph("立ち食い寿司 ゲンヤ倶楽部 1店舗", st["table_text"])],
            [Paragraph("有効期限", st["small"]), Paragraph("2026年11月8日", st["table_text"])],
            [Paragraph("月額支援", st["small"]), Paragraph("遠隔支援と軽微変更は翌月へ繰り越しません。", st["table_text"])],
            [Paragraph("追加作業", st["small"]), Paragraph("内容確認後、着手前に別途見積します。", st["table_text"])],
            [Paragraph("契約条件", st["small"]), Paragraph("正式な条件は申込書または利用契約書に定めます。", st["table_text"])],
        ], colWidths=[28 * mm, 138 * mm], style=[
            ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("BACKGROUND", (0, 0), (0, -1), WARM),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
        Spacer(1, 4 * mm),
        callout("現在のGoogleマップ予約導線は食べログ経由です。Google公式予約API等との新規直接接続は、本見積には含まれません。", st, edge=GREEN, background=colors.HexColor("#edf8f0")),
    ]
    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(PDF_PATH)
