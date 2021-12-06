"""Main module."""

import csv
import shutil
from dataclasses import asdict, dataclass, field
from pathlib import Path
from string import Template

import nanoid
import yaml
from PyPDF4 import PdfFileReader, PdfFileWriter

ITEM_TEMPLATE = """$title
$sub_title

- $item_url
"""

ITEM_PART_TEMPLATE = """
$title
$sub_title

pages: $doc_start_pg-$doc_end_pg

- $item_url
"""


@dataclass
class Item:  # pylint: disable=too-many-instance-attributes
    """Class representing an Item and optional children."""

    title: str
    doc_end_pg: int
    pdf_end_pg: int

    children: list = field(default_factory=list)
    doc_start_pg: int = field(default=1)
    pdf_start_pg: int = field(default=1)
    sub_title: str = field(default="")

    name: str = field(init=False)
    pages: tuple = field(init=False)

    def __post_init__(self):
        """Initilize dynamic members."""
        slug = self.title.lower().replace(' ', '_')

        self.doc_end_pg = int(self.doc_end_pg)
        self.doc_start_pg = int(self.doc_start_pg)
        self.pdf_end_pg = int(self.pdf_end_pg)
        self.pdf_start_pg = int(self.pdf_start_pg)

        self.name = f'{slug}.pdf'
        self.pages = tuple(range(self.pdf_start_pg - 1, self.pdf_end_pg))

    def as_dict(self):
        """Return instance fields as a dictionary."""
        return asdict(self)


def _add_pdf(src, dir_stage, title):

    with Path(src).open('rb') as fd_in:
        reader = PdfFileReader(fd_in)

        end_page = reader.numPages

    item = Item(title=title, doc_end_pg=end_page, pdf_end_pg=end_page)

    shutil.copy(src, (Path(dir_stage) / item.name))

    return item


def _add_pdf_part(src, dir_stage, part):

    with Path(src).open('rb') as fd_in:
        reader = PdfFileReader(fd_in)
        writer = PdfFileWriter()

        for page in part.pages:
            writer.addPage(reader.getPage(page))

        with (Path(dir_stage) / part.name).open('wb') as fd_out:
            writer.write(fd_out)

    return part


def get_id():
    """Return a nanoid string."""
    return nanoid.generate(size=10)


def new_item(src, dir_stage, parts, title):
    """Create a new Item object.

    :param src: path to file to add
    :type src: str
    :param dir_stage: path to staging directory
    :dir_stage: str
    :param title: User friendly title for item
    :type title: str

    :return: Item
    :rtype: Item
    """
    item = _add_pdf(src, dir_stage, title)

    for part in parts:
        item.children.append(_add_pdf_part(src, dir_stage, part))

    return item


def parse_config_file(path, upload_dir):
    """Return config from yaml file at path."""
    with Path(path).expanduser().open(encoding='utf-8') as fd_in:
        cfg = yaml.safe_load(fd_in)
        cfg['upload_dir'] = cfg['upload_dir'] if not upload_dir else upload_dir

        if cfg['upload_dir'][-1] != '/':
            cfg['upload_dir'] = cfg['upload_dir'] + '/'

        return cfg


def parse_parts_file(path):
    """Parse parts file and return a list of Items."""
    parts = []

    try:
        with Path(path).open(encoding='utf-8', newline='') as fd_in:
            reader = csv.DictReader(fd_in)

            for row in reader:
                parts.append(Item(**row))

    except TypeError:
        pass

    return parts


def render_item(item, item_id, item_url_str):
    """Render an item and optional children to a text string."""
    fields = item.as_dict()
    fields['item_url'] = Template(item_url_str).substitute(nid=item_id,
                                                           name=item.name)

    out = Template(ITEM_TEMPLATE).substitute(**fields)

    part_template = Template(ITEM_PART_TEMPLATE)
    item_url_template = Template(item_url_str)

    for child in item.children:
        fields = child.as_dict()
        fields['item_url'] = item_url_template.substitute(nid=item_id,
                                                          name=child.name)
        out += part_template.substitute(**fields)

    return out
