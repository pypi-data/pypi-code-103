"""
HttpRunner html report

- result: define resultclass for unittest TextTestRunner
- gen_report: render html report with jinja2 template

"""

from vhrun3.report.html.gen_report import gen_html_report

__all__ = [
    "gen_html_report"
]