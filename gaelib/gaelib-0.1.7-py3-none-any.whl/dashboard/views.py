from flask import g, render_template, request, session
from gaelib.auth.decorators import auth_required, access_control
from gaelib.auth.models import User, UserRole
from gaelib.env import (get_dashboard_url_prefix,
                        get_env,
                        get_post_login_page,
                        get_sidebar_template)
from gaelib.view.base_view import BaseHttpHandler
from gaelib.utils.web import app


class DashboardView(BaseHttpHandler):
  decorators = [access_control(role=UserRole.STAFF), auth_required]
  methods = ['GET', 'POST']


class DashboardLogin(BaseHttpHandler):
  """
      The solo view function to get all the game entities
      matching the filters passed
  """
  methods = ['GET']

  def dispatch_request(self):
    return render_template("login.html",
                           post_login_page=get_post_login_page()
                           )


class DashboardLogout(BaseHttpHandler):
  """
      The solo view function to get all the game entities
      matching the filters passed
  """
  methods = ['GET']

  def dispatch_request(self):
    try:
      session.pop("gae_uid")
    except KeyError:
      pass
    return render_template("logout.html")


class Notifications(DashboardView):
  """
      The solo view function to get all the game entities
      matching the filters passed
  """
  methods = ['GET', 'POST']

  def dispatch_request(self):
    if request.method == 'GET':
      return render_template("notifications.html")
