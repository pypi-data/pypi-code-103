from apps.task.api_views import api_view
from flask import Blueprint
from flask_restful_helper import Api

blueprint = Blueprint('task', __name__, url_prefix='/task')
api = Api(blueprint)

api.add_resource(api_view.Task, '/tasks', endpoint='tasks', methods=['GET', 'POST'])
api.add_resource(api_view.Task, '/tasks/<pk>', endpoint='tasks_pk', methods=['GET', 'PUT', 'PATCH', 'DELETE'])

api.add_resource(api_view.TaskLog, '/task_logs/<pk>', endpoint='task_logs', methods=['GET', 'DELETE'])
