"""Generates PDF cards from a calibre metadata.db."""

import os
import shutil
from pathlib import Path
from textwrap import shorten

from calibrestekje import Book, Comment, Publisher, init_session
from reportlab.lib.pagesizes import *
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

CWD = Path().resolve()


def make_cards(filepath, db_path, side_a, side_b):
    """The main entrypoint for card generation."""
    filename = os.path.basename(filepath)
    doc = create_doc(filename)
    content = get_fields(db_path, side_a, side_b)
    doc.build(content)
    shutil.move(os.path.join(CWD, filename), filepath)


def select_fields(fields, content, styles, book):
    if "title" in fields:
        tag = "<font size=12>{}</font>".format(book.title)
        ptitle = Paragraph(tag, styles["Italic"])
        content.append(ptitle)
        content.append(Spacer(1, 12))

    if "timestamp" in fields:
        tag = "<font size=10>Timestamp: {}</font>".format(book.timestamp)
        ptime = Paragraph(tag, styles["Normal"])
        content.append(ptime)
        content.append(Spacer(1, 12))

    if "comments" in fields:
        comments = ", ".join(
            [
                shorten(comment.text, width=50, placeholder="...")
                for comment in book.comments
            ]
        )
        tag = "<font size=10>{}</font>".format(comments)
        pcomments = Paragraph(tag)
        content.append(pcomments)

    if "authors" in fields:
        format_string = "<font size=12>{}</font>"
        all_authors = [author.name for author in book.authors]
        glued_together = format_string.format(", ".join(all_authors))

        p = Paragraph(glued_together, styles["Normal"])
        content.append(p)
        content.append(Spacer(6, 12))

    if "tags" in fields:
        format_string = "<font size=10>{}</font>"
        all_tags = [tag.name for tag in book.tags]
        tags_glued_together = format_string.format(", ".join(all_tags))

        p = Paragraph(tags_glued_together, styles["Normal"])
        content.append(p)
        content.append(Spacer(6, 12))

    return content


def get_fields(db_path, side_a, side_b):
    """Retrieve fields from the metadata."""
    content = []
    styles = getSampleStyleSheet()
    session = init_session(db_path)

    for book in session.query(Book).all():
        content = select_fields(side_a, content, styles, book)
        content.append(PageBreak())
        content = select_fields(side_b, content, styles, book)
        content.append(PageBreak())

    return content


def create_doc(filename):
    """Build the Report Lab document template."""
    return SimpleDocTemplate(
        filename,
        pagesize=landscape(A6),
        rightMargin=18,
        leftMargin=18,
        topMargin=0,
        bottomMargin=18,
    )
