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
from flask import send_file, Response
from flask_security import current_user
from flask_security import login_required
from flask_security import permissions_required
from flask_security import permissions_accepted
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired

from flask import current_app
from sqlalchemy import and_
from . import models
from .util.mail import send_bulk_mail
from .util.helpers import get_object_from_arg

ITEMS_PER_PAGE = 25

# Create the web blueprint
bp = Blueprint('web', __name__)


@bp.app_errorhandler(404)
def page_not_found_error(error):
    title = f'PIDB: 404 Not Found'
    return render_template('error/notfound.html', title=title), 404


@bp.errorhandler(403)
def forbidden_error(error):
    title = f'PIDB: 403 Forbidden'
    return render_template('error/forbidden.html', title=title), 404


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')

@bp.route('/findings')
@login_required
def web_findings():
    page = request.args.get('page', 1, type=int)
    findings = models.Finding.query.filter\
            (models.Finding.deleted.is_(None)).\
            order_by(models.Finding.finding_id.asc()).\
            paginate(page=page, per_page=ITEMS_PER_PAGE)

    subjects = models.Subject.query.order_by\
            (models.Subject.subject_id.asc()).all()
    experiments = models.Experiment.query.join\
                (models.Finding, models.Finding.experiment_id == models.Experiment.experiment_id).all()
    labels = models.Label.query.order_by\
            (models.Label.label_id.asc()).all()

    return render_template('findings.html',\
                        findings=findings,\
                        experiments=experiments,\
                        labels=labels, \
                        subjects=subjects)

@bp.route('/finding/<int:id>')
@login_required
def web_finding(id):
    finding = models.Finding.query.filter\
            (models.Finding.finding_id == id).one_or_none()
    properties = models.Property.query.join\
                (models.Finding, models.Finding.finding_id == models.Property.finding_id)\
                .filter(models.Finding.finding_id == id).all()

    return render_template('finding.html',\
                        finding=finding,\
                        properties=properties)

@bp.route('/experiments')
@login_required
def web_experiments():
    page = request.args.get('page', 1, type=int)
    finding_templates = models.Finding.query.group_by\
                        (models.Finding.task_template).all()

    labels = models.Label.query.order_by\
            (models.Label.label_id.asc()).all()

    subjects = models.Subject.query.order_by\
            (models.Subject.subject_id.asc()).all()
    # Default experiments are finding label__main__ ...
    experiments = models.Experiment.query.filter\
                (models.Experiment.findings.any())\
                .paginate(page=page, per_page=ITEMS_PER_PAGE)

    findings = models.Finding.query.filter\
            (models.Finding.deleted.is_(None)).\
            order_by(models.Finding.finding_id.asc()).all()

    return render_template('experiments.html',\
                        finding_templates=finding_templates,\
                        labels=labels,\
                        experiments=experiments,\
                        findings=findings,\
                        subjects=subjects,\
                        experiments_for_template=False)

@bp.route('/experiments/<string:template>')
@login_required
def web_experiments_template(template):
    page = request.args.get('page', 1, type=int)
    finding_templates = models.Finding.query.group_by\
                    (models.Finding.task_template)\
                    .filter(models.Finding.deleted.is_(None)).all()

    labels = models.Label.query.join\
            (models.Finding, models.Finding.label_id == models.Label.label_id)\
            .filter(and_(models.Finding.deleted.is_(None),\
            models.Finding.task_template == template)).all()

    subjects = models.Subject.query.order_by\
            (models.Subject.subject_id.asc()).all()

    experiments =  models.Experiment.query.join\
                (models.Finding, models.Finding.experiment_id == models.Experiment.experiment_id)\
                .filter(models.Finding.task_template == template)\
                .paginate(page=page, per_page=ITEMS_PER_PAGE)

    findings = models.Finding.query.order_by(models.Finding.finding_id.asc()).all()
    return render_template('experiments.html',\
                        finding_templates=finding_templates,\
                        labels=labels,\
                        experiments=experiments,\
                        findings=findings,\
                        subjects=subjects,\
                        template=template)

@bp.route('/experiment/<int:id>')
@login_required
def web_experiment(id, template=None):
    experiment = models.Experiment.query.filter\
                (models.Experiment.experiment_id == id).one_or_none()

    resources = models.Experiment.query.join\
                (models.XnatResource, models.Experiment.experiment_id == models.XnatResource.experiment_id)\
                .filter(models.Experiment.experiment_id == id).all()

    finding_templates = models.Finding.query.group_by\
                    (models.Finding.task_template)\
                    .filter(models.Finding.experiment_id == id).all()

    if template is None:
        findings = models.Finding.query.filter\
                  (and_(models.Finding.deleted. is_(None),\
                  models.Finding.experiment_id == id)).all()

        labels = models.Label.query.join\
                (models.Finding, models.Finding.label_id == models.Label.label_id)\
                .filter(models.Finding.experiment_id == id).all()

        properties = models.Property.query.join\
                (models.Finding, models.Finding.finding_id == models.Property.finding_id)\
                .filter(models.Finding.experiment_id == id).all()
    else:   
        findings = models.Finding.query.filter\
            (and_(models.Finding.deleted.is_(None),\
            models.Finding.experiment_id == id,\
            models.Finding.task_template == template)).all()

        labels = models.Label.query.join\
                (models.Finding, models.Finding.label_id == models.Label.label_id)\
                .filter(_and(models.Finding.experiment_id == id),\
                 models.Finding.task_template == template).all()

        properties = models.Property.query.join(models.Finding,\
                models.Finding.finding_id == models.Property.finding_id)\
                .filter(_and(models.Finding.experiment_id == id), \
                models.Finding.task_template == template).all()

    return render_template('experiment.html',\
                        experiment=experiment,\
                        resources=resources,\
                        findings=findings,\
                        labels=labels,\
                        properties=properties,\
                        templates= finding_templates)

@bp.route("/getCSV")
def getCSV():

    headers = ["experiment id", "subject id", "scan date"]
    csv_data = ''
    filename = 'overview.csv'

    labels = models.Label.query.order_by\
            (models.Label.label_id.asc()).all()

    experiments = models.Experiment.query.join\
                (models.Finding, models.Finding.experiment_id == models.Experiment.experiment_id).all()

    findings = models.Finding.query.order_by\
                (models.Finding.finding_id.asc()).all()

    for label in labels:
        headers.append(label.label_text)
    headers = ','.join(headers) + '\n'

    
    for experiment in experiments:
        data = [str(experiment.experiment_id), str(experiment.subject_id), str(experiment.date)]
        for label in labels:
            findings = models.Finding.query.join\
                    (models.Experiment, models.Finding.experiment_id == models.Experiment.experiment_id) \
                    .filter(and_(models.Finding.experiment_id == experiment.experiment_id,\
                    models.Finding.label_id == label.label_id)).all()

            data.append(str(len(findings)))
        csv_data += ','.join(data) + '\n'
    
    csv = headers + csv_data
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                "attachment; filename=overview.csv"})

@bp.route("/getCSV/<int:id>")
def getCSV_finding(id):

    headers = ["experiment id", "subject id", "scan date"]
    csv_data = ''

    label = models.Label.query.filter\
            (models.Label.label_id == id).one_or_none()

    findings = models.Finding.query.filter\
            (models.Finding.label_id == label.label_id).all() 

    properties = models.Property.query.join\
                (models.Finding, models.Property.finding_id == models.Finding.finding_id)\
                .filter(models.Finding.label_id == label.label_id).all()

    main_prop = set()
    for prop in properties:
        main_prop.add(prop.label)
    headers = ','.join(headers + list(main_prop)) + '\n'

    for finding in findings:
        experiment = models.Experiment.query.join\
                    (models.Finding, models.Finding.experiment_id == models.Experiment.experiment_id)\
                    .filter(models.Finding.finding_id == finding.finding_id).one()

        subject = models.Subject.query.filter_by\
                (subject_id = experiment.subject_id).one()

        props = models.Property.query.filter_by\
            (finding_id = finding.finding_id).all()

        value_dict = {}
        if experiment is not None:
            data = [str(experiment.label), str(subject.study_id), str(experiment.date)]

            for prop in props:
                value = str(prop.value)
                if ',' in value:
                    value = value.replace(',', '/')
                value_dict[prop.label] = value

            for prop in main_prop:
                if prop in value_dict:
                    data.append(str(value_dict[prop]))
                else:
                    data.append("-")

            csv_data += ','.join(data) + '\n'

    csv = headers + csv_data
    file_name = label.label_text
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                f'attachment; filename={file_name}.csv'})


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


class MailForm(FlaskForm):
    recipients = SelectMultipleField('Recipients')
    subject = TextField('Subject', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

    @bp.route("/mail", methods=['GET', 'POST'])
    @login_required
    @permissions_accepted('user_read_all')
    def mail():
        form = MailForm(request.form)

        form.recipients.choices = ((u.username, f'{u.name} <{u.email}>') for u in models.User.query.all())

        if form.validate_on_submit():
            recipients = form.recipients.data
            subject = form.subject.data
            body = form.body.data

            if recipients:
                recipients = [get_object_from_arg(x, models.User, models.User.username, skip_id=True) for x in recipients]
            else:
                recipients = models.User.query.all()

            send_bulk_mail(
                recipients=recipients,
                subject=subject,
                body=body,
            )
            return render_template('mail_sent.html',
                                   recipients=recipients,
                                   subject=subject,
                                   body=body)

        return render_template('mail.html', mail_form=form)
