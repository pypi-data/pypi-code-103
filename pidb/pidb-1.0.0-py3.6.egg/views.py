# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import abort
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_security import current_user
from flask_security import login_required
from flask_security import permissions_required
from flask_security import permissions_accepted

from flask import current_app

from . import models


# Create the web blueprint
bp = Blueprint('web', __name__)


@bp.app_errorhandler(404)
def page_not_found_error(error):
    title = f'Taskmanager: 404 Not Found'
    return render_template('error/notfound.html', title=title), 404


@bp.errorhandler(403)
def forbidden_error(error):
    title = f'Taskmanager: 403 Forbidden'
    return render_template('error/forbidden.html', title=title), 404


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/findings')
@login_required
def web_findings():
    findings = models.Finding.query.order_by(models.Finding.finding_id.asc()).all()
    experiments = models.Experiment.query.join(models.Finding, models.Finding.experiment_id == models.Experiment.experiment_id).all()
    labels = models.Label.query.order_by(models.Label.label_id.asc()).all()
    return render_template('findings.html', findings=findings, experiments=experiments, labels=labels)

@bp.route('/finding/<int:id>')
@login_required
def web_finding(id):
    finding = models.Finding.query.filter(models.Finding.finding_id == id).one_or_none()
    properties = models.Property.query.join(models.Finding, models.Finding.finding_id == models.Property.finding_id)\
        .filter(models.Finding.finding_id == id).all()
    return render_template('finding.html', finding=finding, properties=properties)

@bp.route('/experiment/<int:id>')
@login_required
def web_experiment(id):
    experiment = models.Experiment.query.filter(models.Experiment.experiment_id == id).one_or_none()
    resources = models.Experiment.query.join(models.XnatResource, models.Experiment.experiment_id == models.XnatResource.experiment_id)\
        .filter(models.Experiment.experiment_id == id).all()
    return render_template('experiment.html', experiment=experiment, resources=resources)

@bp.route('/users')
@login_required
@permissions_accepted('roles_manage')
def users():
    data = models.User.query.all()
    roles = models.Role.query.order_by(models.Role.id).all()
    return render_template('userroles.html', data=data, roles=roles)


@bp.route('/users/<int:id>')
@login_required
def user(id):
    data = models.User.query.filter(models.User.id == id).one_or_none()
    if data is None:
        abort(404)

    if not current_user.has_permission('user_read_all'):
        # This is a normal user, so may only see own user information.
        if current_user != data:
            abort(403)

    return render_template('user.html', data=data)
