import copy
import os
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table
from svglib.svglib import svg2rlg

# always available fonts: Courier, Courier-Bold, Courier-BoldOblique, Courier-Oblique, Helvetica, Helvetica-Bold,
# Helvetica-BoldOblique, Helvetica-Oblique, Symbol, Times-Bold, Times-BoldItalic, Times-Italic, Times-Roman,
# ZapfDingbats
# default reportlab font: Helvetica

gdata = {}


class PageCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.before_save()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def before_save(self):
        num_pages = len(self._saved_page_states)

        self.setFont("Helvetica", 8)
        self.setFillColorCMYK(0, 0, 0, 0.75)

        self.drawRightString(
            A4[0] - (25 * mm), 15 * mm, f"Page {self._pageNumber}/{num_pages}"
        )

        self.drawString(
            25 * mm,
            18 * mm,
            gdata["footer"][0],
        )

        self.drawString(
            25 * mm,
            15 * mm,
            gdata["footer"][1],
        )


def get_svg(path, sx=1, sy=1):
    svg = svg2rlg(path)
    svg.width, svg.height = svg.minWidth() * sx, svg.height * sy
    svg.scale(sx, sy)
    return svg


def address_table(data, style):
    receiver = [
        x
        for x in [
            data["company"],
            data["name"],
            " ",
            data["address1"],
            data["address2"],
            data["city"] + ", " + data["state"] + " " + data["zip_code"],
            data["country"],
        ]
        if x is not None and x != ""
    ]

    t = Table(
        [
            [Paragraph("<br/>".join(receiver), style)],
        ],
        colWidths=["100%"],
        style=[],
    )
    return t


def create(d):
    global gdata
    gdata = d
    buffer = BytesIO()
    styles = getSampleStyleSheet()
    style_normal = copy.copy(styles["BodyText"])

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=d["type"],
        creator=d["creator"],
        pageCompression=1,
        topMargin=10 * mm,
        leftMargin=25 * mm,
        rightMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    color_gray_light = colors.CMYKColor(0, 0, 0, 0.1)
    color_gray = colors.CMYKColor(0, 0, 0, 0.75)

    style_item_header = copy.copy(styles["BodyText"])

    style_normal_right = copy.copy(styles["BodyText"])
    style_normal_right.alignment = 2

    style_document_header = copy.copy(styles["BodyText"])
    style_document_header.fontSize = 18
    style_document_header.alignment = 1

    style_item_description = copy.copy(styles["BodyText"])
    style_item_description.fontSize = 8
    style_item_description.textColor = color_gray

    flow = []
    flow.append(
        Table(
            [
                [
                    "",
                    get_svg(
                        os.path.join(
                            os.path.dirname(__file__), "data/invoice_logo.svg"
                        ),
                        3,
                        3,
                    ),
                ],
            ],
            colWidths=["50%", "50%"],
            style=[
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("BOTTOMPADDING", (0, 0), (1, 0), 20 * mm),
            ],
        )
    )
    flow.append(address_table(d["to"], style_normal))
    flow.append(
        Table(
            [
                ["", d["type"].upper()],
                ["", "Date"],
                ["", d["date"]],
            ],
            colWidths=["50%", "60%"],
            style=[
                ("ALIGN", (1, 0), (1, 2), "RIGHT"),
                ("FONTSIZE", (1, 0), (1, 0), 18),
                ("TEXTCOLOR", (1, 1), (1, 1), color_gray),
                ("BOTTOMPADDING", (0, 0), (1, 0), 10 * mm),
                ("BOTTOMPADDING", (0, 2), (1, 2), 10 * mm),
            ],
        )
    )

    style = [
        ("BACKGROUND", (0, 0), (2, 0), color_gray_light),
        ("TEXTCOLOR", (0, 0), (2, 0), color_gray),
    ]

    amount_sum = 0
    num_rows = 1
    data = [["Item", "", "Total"]]
    for item in d["items"]:
        data.append(
            [
                (
                    Paragraph(item["name"], style_item_header),
                    Paragraph(item["description"], style_item_description),
                ),
                "",
                d["currency_symbol"]
                + " "
                + (str(item["amount"]) if item["amount"] else "0"),
            ]
        )
        amount_sum += item["amount"]

        style.append(("LINEBELOW", (0, num_rows), (2, num_rows), 1, color_gray_light))
        num_rows += 1

    data.append(
        ["", "Total", d["currency_symbol"] + " " + "%.2f" % round(amount_sum, 2)]
    )

    num_rows += 2
    style.append(("ALIGN", (0, 0), (0, num_rows), "LEFT"))
    style.append(("ALIGN", (1, 0), (2, num_rows), "RIGHT"))
    style.append(("TEXTCOLOR", (0, num_rows - 2), (1, num_rows), color_gray))
    flow.append(Table(data, colWidths=["70%", "15%", "15%"], repeatRows=1, style=style))

    doc.build(flow, canvasmaker=PageCanvas)
    buffer.seek(0)
    return buffer
