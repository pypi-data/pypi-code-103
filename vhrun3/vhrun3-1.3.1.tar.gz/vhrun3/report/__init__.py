"""
HttpRunner report

- summarize: aggregate test stat data to summary
- stringify: stringify summary, in order to dump json file and generate html report.
- html: render html report
"""


from vhrun3.report.html.gen_report import gen_html_report

__all__ = [
    "gen_html_report"
]
