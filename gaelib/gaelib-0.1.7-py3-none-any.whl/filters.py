import flask

blueprint = flask.Blueprint('filters', __name__)

# using the decorator
@blueprint.app_template_filter()
def datetime_difference(date1, date2):
  return int(((date2 - date1).total_seconds())/60)
