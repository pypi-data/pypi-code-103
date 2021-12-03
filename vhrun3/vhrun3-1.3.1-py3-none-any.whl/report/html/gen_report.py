import io
import json
import os
from datetime import datetime
from jinja2 import Template
from loguru import logger


def gen_html_report(summary, report_template=None, report_dir=None, report_name=None) -> str:
    """ render html report with specified report name and template

    Args:
        summary (dict): test result summary data
        report_template (str): specify html report template path, template should be in Jinja2 format.
        report_dir (str): specify html report save directory
        report_name (str): report name.

    """
    # if not summary["time"] or summary["stat"]["testcases"]["total"] == 0:
    #     logger.log_error("test result summary is empty ! {}".format(summary))
    #     raise SummaryEmpty

    if not report_template:
        report_template = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "template.html"
        )
        # logger.debug("No html report template specified, use default.")
    else:
        logger.info("render with html report template: {}".format(report_template))

    logger.info("1, Start to render Html report ...")

    start_at_timestamp = summary["time"]["start_at"]
    # utc_time_iso_8601_str = datetime.utcfromtimestamp(start_at_timestamp).isoformat()
    utc_time_iso_8601_str = datetime.fromtimestamp(start_at_timestamp).strftime('%Y_%m_%d_%H_%M_%S')
    utc_time_iso_8601_str = os.environ["test_start_time"] if "test_start_time" in os.environ else utc_time_iso_8601_str
    summary["time"]["start_datetime"] = datetime.fromtimestamp(start_at_timestamp).strftime('%Y/%m/%d %H:%M:%S')

    report_dir = report_dir or os.path.join(os.getcwd(), "reports")
    if report_name:
        report_file_name = report_name
    else:
        # fix #826: Windows does not support file name include ":"
        report_file_name = "{}.html".format(utc_time_iso_8601_str.replace(":", "").replace("-", ""))

    if not os.path.isdir(report_dir):
        os.makedirs(report_dir)

    report_path = os.path.join(report_dir, report_file_name)
    with io.open(report_template, "r", encoding='utf-8') as fp_r:
        template_content = fp_r.read()
        with io.open(report_path, 'w', encoding='utf-8') as fp_w:
            rendered_content = Template(
                template_content,
                extensions=["jinja2.ext.loopcontrols"]
            ).render(summary)
            fp_w.write(rendered_content)

    logger.info("1, Generated Html report: {}".format(report_path))
    os.environ["report_path"] = report_path

    json_file_name = "{}.json".format(utc_time_iso_8601_str.replace(":", "").replace("-", ""))
    json_file_path = os.path.join(report_dir, json_file_name)
    # with open(json_file_path, "w") as f:
    #     f.write(json.dumps(summary))

    return report_path

