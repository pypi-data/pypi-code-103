from gaelib.view.base_view import BaseHttpHandler

from flask import g, request


class LogApi(BaseHttpHandler):
  """
      The contest home view function to get the previous contest winner
  """

  def dispatch_request(self):
    data = request.get_json()
    if 'logs' in data:
      for log in data['logs']:
        # Removing the timestamp and loglevel
        # from the client. We can add timestamp later if needed
        message = log['msg'][32:]
        if log['level'] == 'info':
          g.app.logger.info(message)
        elif log['level'] == 'debug':
          g.app.logger.debug(message)

    return self.json_success({}, 200)