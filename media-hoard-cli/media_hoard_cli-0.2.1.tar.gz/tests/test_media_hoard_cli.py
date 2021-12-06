#!/usr/bin/env python
"""Tests for `media_hoard_cli` package."""
# pylint: disable=redefined-outer-name
from click.testing import CliRunner

from media_hoard_cli import cli, hoard

ITEM_NID = 'YKIKuCiQAl'


def test_item_init():
    """Test Item init."""
    item = hoard.Item(title="Simple PDF File", doc_end_pg=2, pdf_end_pg=2)

    assert item.title == "Simple PDF File"
    assert item.sub_title == ""
    assert item.pdf_start_pg == 1
    assert item.pdf_end_pg == 2
    assert item.doc_start_pg == 1
    assert item.doc_end_pg == 2
    assert item.name == "simple_pdf_file.pdf"
    assert item.pages == (0, 1)
    assert len(item.children) == 0

    args = {
        'title': "Chapter 1",
        'sub_title': "Detailed Nonsense",
        'doc_start_pg': 12,
        'doc_end_pg': 14,
        'pdf_start_pg': 14,
        'pdf_end_pg': 16
    }

    item = hoard.Item(**args)

    assert item.sub_title == "Detailed Nonsense"
    assert item.doc_start_pg == 12
    assert item.doc_end_pg == 14
    assert item.pdf_start_pg == 14
    assert item.pdf_end_pg == 16


def test_cli_missing_add_file():
    """Test exception text on missing input file."""
    runner = CliRunner()

    result = runner.invoke(cli.main, [
        'add', '--cfg-file', 'tests/fixtures/config.yaml',
        'Input File Not Found', '/no_such_file.pdf'
    ])

    assert result.exit_code == 1
    assert "/no_such_file.pdf" in result.output


def test_cli_add_pdf(mocker, tmp_path):
    """Test adding a single file."""
    mocker.patch('media_hoard_cli.hoard.nanoid.generate',
                 return_value=ITEM_NID)
    runner = CliRunner()
    result = runner.invoke(cli.main, [
        'add', '--cfg-file', 'tests/fixtures/config.yaml', '--upload-dir',
        tmp_path, 'Basic Test File', 'tests/fixtures/file.pdf'
    ])

    assert result.exit_code == 0
    assert (tmp_path / ITEM_NID / 'basic_test_file.pdf').is_file()

    expected = """Basic Test File


- http://localhost/YKIKuCiQAl/basic_test_file.pdf

"""

    assert result.output == expected


def test_cli_add_pdf_parts(mocker, tmp_path):
    """Test adding a pdf file and parts."""
    mocker.patch('media_hoard_cli.hoard.nanoid.generate',
                 return_value=ITEM_NID)
    runner = CliRunner()
    result = runner.invoke(cli.main, [
        'add', '--cfg-file', 'tests/fixtures/config.yaml', '--part-file',
        'tests/fixtures/file_parts.csv', '--upload-dir', tmp_path,
        'Basic Test File', 'tests/fixtures/file_with_parts.pdf'
    ])

    print(result.output)
    assert result.exit_code == 0
    assert (tmp_path / ITEM_NID / 'introduction.pdf').is_file()

    expected = """Basic Test File


- http://localhost/YKIKuCiQAl/basic_test_file.pdf

Introduction


pages: 1-2

- http://localhost/YKIKuCiQAl/introduction.pdf

Chapter 1


pages: 3-6

- http://localhost/YKIKuCiQAl/chapter_1.pdf

Chapter 3
Nonsense, more nonsense, and silliness

pages: 9-11

- http://localhost/YKIKuCiQAl/chapter_3.pdf

"""

    assert result.output == expected
