import textwrap
import json
import traceback

from flask import Blueprint, current_app
from flask_graphql import GraphQLView

from .. import auth, schema, ops
from .graphql_ide import GRAPHIQL_NEWER, GRAPHQL_PLAYGROUND

##__________________________________________________________________||
from flask import request


def format_to_str(data_dict):

    format_item = textwrap.dedent(
        """
        - {key}:
        {value}
        """
    ).lstrip()

    return "\n".join(
        [
            format_item.format(
                key=k,
                value=textwrap.indent(str(v), " " * 4).rstrip(),
            )
            for k, v in data_dict.items()
        ]
    )


class GraphQLView(GraphQLView):
    def dispatch_request(self):
        res = super().dispatch_request()
        # return res

        if isinstance(res, str):
            # e.g, GraphiQL
            return res

        try:
            self._log_response(res)
        except BaseException:
            traceback.print_exc()
        finally:
            return res

    def _log_response(self, res):
        if res.status_code == 200:
            return

        level = "ERROR"

        try:
            msg = self._compose_message(res)
        except BaseException:
            msg = traceback.format_exc()

        # print(msg)
        # print()

        ops.create_log(level=level, message=msg)
        ops.commit()

    def _compose_message(self, res):
        content = {
            "Request": self._format_request_to_str(),
            "Response": self._format_response_to_str(res),
        }
        msg = format_to_str(content)
        return msg

    def _format_request_to_str(self):
        content = {
            "Header": str(request.headers),
            "Data": format_to_str(self.parse_body()),
        }
        msg = format_to_str(content)
        # print(msg)
        return msg

    def _format_response_to_str(self, response):
        content = {
            "Status": str(response.status),
            "Data": textwrap.indent(
                json.dumps(response.get_json(), indent=2),
                " " * 4,
            ),
        }
        msg = format_to_str(content)
        return msg


class GraphQLViewW(GraphQLView):
    """A wrapper of GraphQLView.

    Used to determine arguments to GraphQLView.as_view() for each view
    based on on the configuration and request.

    The usual usage of GraphQLView in add_url_rule() as in the document
    (https://github.com/graphql-python/flask-graphql/tree/v2.0.1#usage) is
    as follows
      bp.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

    The arguments (schema, graphiql) need to have already been
    determined when the module is imported. In this app, they have not
    because they depend on the configuration and request.

    The __init__() will be called in each view from
    https://github.com/pallets/flask/blob/1.1.2/src/flask/views.py#L88

    The arguments are determined in In __init__() and given to the
    base class GraphQLView.

    """

    def __init__(self, **kwargs):
        kwargs.update(
            {
                "schema": _select_schema(),
                "graphiql": current_app.config.get("ACONDBS_GRAPHIQL", False),
                "graphiql_template": _select_graphiql_template(),
            }
        )
        super().__init__(**kwargs)


##__________________________________________________________________||
bp = Blueprint("graphql", __name__)
bp.add_url_rule("/graphql", view_func=GraphQLViewW.as_view("graphql"))


def init_app(app):
    app.register_blueprint(bp)


##__________________________________________________________________||
def _select_schema():
    if auth.is_admin():
        return schema.schema_admin
    elif auth.is_signed_in():
        return schema.schema_private
    else:
        return schema.schema_public


def _select_graphiql_template():
    template_no = current_app.config.get("ACONDBS_GRAPHIQL_TEMPLATE_NO", None)
    if template_no == 1:
        return GRAPHIQL_NEWER
    elif template_no == 2:
        return GRAPHQL_PLAYGROUND
    else:
        return None


##__________________________________________________________________||
