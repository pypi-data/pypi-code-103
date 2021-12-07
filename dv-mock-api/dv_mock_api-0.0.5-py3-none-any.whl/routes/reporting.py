from flask import Blueprint, send_from_directory, request
from dv_mock_api.models.report import Report
from dv_mock_api.settings import REPORT_DIRECTORY


reporting_blueprint = Blueprint('reporting', __name__,)


@reporting_blueprint.route('/doubleclickbidmanager/v1.1/query/<query_id>', methods=["GET"])
def get_query(query_id):
    base = request.base_url.replace(
        f"/doubleclickbidmanager/v1.1/query/{query_id}", "")
    return Report(query_id=query_id, base_url=base).get()


@reporting_blueprint.route('/doubleclickbidmanager/v1.1/query/<query_id>', methods=["POST"])
def run_query(query_id):
    base = request.base_url.replace(
        f"/doubleclickbidmanager/v1.1/query/{query_id}", "")
    _, status_code = Report(query_id=query_id, base_url=base).run()
    return {}, status_code


@reporting_blueprint.route('/doubleclickbidmanager/v1.1/query', methods=["POST"])
def create_query():
    base = request.base_url.replace(f"/doubleclickbidmanager/v1.1/query", "")
    return Report(base_url=base, create_query=True).create()


@reporting_blueprint.route('/download/<path:path>')
def download(path):
    path = path.split('.')[0]
    report_object = Report(
        query_id=path, base_url=request.base_url
    )
    report_message, status_code = report_object.download()
    if not report_object.file_name:
        return report_message, status_code
    return send_from_directory(REPORT_DIRECTORY, report_object.file_name), status_code
