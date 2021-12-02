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

import datetime
import json
import urllib.parse


from flask import Blueprint, abort, jsonify, request
from flask_restplus import Api, Resource, inputs, reqparse, fields
from flask_security import auth_required, current_user, http_auth_required, permissions_accepted, permissions_required
from flask_security.utils import hash_password
import marshmallow
from sqlalchemy import and_
from sqlalchemy.ext.declarative import DeclarativeMeta

from . import RegisteredApi
from .. import exceptions
from .. import models
from .. import control
from .. import user_datastore
from ..fields import ObjectUrl, SubUrl
from ..util.helpers import get_object_from_arg

db = models.db

blueprint = Blueprint('api_v1', __name__)

authorization = {
    'basic_auth': {'type': 'basic'}
}

api = RegisteredApi(
    blueprint,
    version='1.0',
    title='Population Imaging Database REST API',
    description='The Population Imaging Database is for storing the results of population imaging studies.',
    default_mediatype='application/json',
    authorization=authorization,
    security='basic_auth'
)


def json_type(data):
    """
    A simple type for request parser that just takes all json as is
    """
    return data


def int_or_str(value):
    return value if isinstance(value, int) else str(value)


def list_of_int_or_str(value):
    if not isinstance(value, list):
        value = list(value)
    return [int_or_str(x) for x in value]
    

def has_permission_any(*args):
    return any(current_user.has_permission(perm) for perm in args)


def has_permission_all(*args):
    return all(current_user.has_permission(perm) for perm in args)


class FindingSchema(marshmallow.Schema):
    finding_id = marshmallow.fields.Int()
    experiment_id = marshmallow.fields.Int()
    label_id = marshmallow.fields.Int()
    generator_url = marshmallow.fields.String(validate=lambda s: len(s) <= 512)
    task_template = marshmallow.fields.String(validate=lambda s: 0 < len(s) < 255)

    @marshmallow.post_load
    def make(self, data):
        if 'finding_id' in data:
            # if we have an experiment_id load from db
            finding = db.session.query(models.Finding).filter(models.Finding.finding_id == data['finding_id']).first()
        else:
            # else create new object
            finding = models.Finding()

        db.session.commit()

        # update fields based on data
        for field in data:
            setattr(finding, field, data[field])

        return finding


class XnatResourceSchema(marshmallow.Schema):
    xnatresource_id = marshmallow.fields.Int()

    url = marshmallow.fields.String(validate=lambda s: len(s) <= 2048)
    hash = marshmallow.fields.String(validate=lambda s: len(s) <= 32)

    finding_id = marshmallow.fields.Int()

    @marshmallow.post_load
    def make(self, data):
        if 'xnatresource_id' in data:
            # if we have an experiment_id load from db
            label = db.session.query(models.XnatResource).filter(models.XnatResource.xnat_resource_id == data['xnatresource_id']).first()
        else:
            # else create new object
            label = models.XnatResource()

        db.session.commit()

        # update fields based on data
        for field in data:
            setattr(label, field, data[field])

        return label


class ExperimentSchema(marshmallow.Schema):
    experiment_id = marshmallow.fields.Int()
    subject_id = marshmallow.fields.Int()
    date = marshmallow.fields.DateTime()

    xnat_resources = marshmallow.fields.Nested(XnatResourceSchema(many=True))
    findings = marshmallow.fields.Nested(FindingSchema(many=True))

    @marshmallow.post_load
    def make(self, data):
        if 'experiment_id' in data:
            # if we have an experiment_id load from db
            experiment = db.session.query(models.Experiment).filter(models.Experiment.experiment_id == data['experiment_id']).first()
        elif 'subject_id' in data and 'date' in data:
            experiment = db.session.query(models.Experiment).filter(
                and_(
                    models.Experiment.subject_id == data['subject_id'],
                    models.Experiment.date == data['date']
                )
            ).first()
            if experiment is None:
                experiment = models.Experiment()
        else:
            # else create new object
            experiment = models.Experiment()

        db.session.commit()

        # update fields based on data
        for field in data:
            setattr(experiment, field, data[field])

        return experiment


class LabelSchema(marshmallow.Schema):
    label_id = marshmallow.fields.Int()
    label_text = marshmallow.fields.String(validate=lambda s: len(s) < 255)

    @marshmallow.post_load
    def make(self, data):
        if 'label_id' in data and data['label_id'] is not None:
            # if we have an experiment_id load from db
            label = db.session.query(models.Label).filter(models.Label.label_id == data['label_id']).first()
        elif 'label_text' in data and len(data['label_text']) > 0:
            label = db.session.query(models.Label).filter(models.Label.label_text == data['label_text']).first()

            if not label:
                label = models.Label()
        else:
            # else create new object
            label = models.Label()

        db.session.commit()

        # update fields based on data
        for field in data:
            setattr(label, field, data[field])

        return label


class PropertySchema(marshmallow.Schema):
    property_id = marshmallow.fields.Int()
    label = marshmallow.fields.String(validate=lambda s: len(s) < 255)
    value = marshmallow.fields.String(validate=lambda s: len(s) < 65535)

    finding_id = marshmallow.fields.Int()

    @marshmallow.post_load
    def make(self, data):
        if 'property_id' in data:
            # if we have an experiment_id load from db
            property = db.session.query(models.Property).filter(models.Property.property_id == data['property_id']).first()
        elif 'finding_id' in data and 'label' in data:
            # load from db by finding_id and label
            property = db.session.query(models.Property).filter(
                and_(
                    models.Property.finding_id == data['finding_id'],
                    models.Property.label == data['label']
                )
            ).first()

            if property is None:
                property = models.Property()
        else:
            # else create new object
            property = models.Property()

        db.session.commit()

        # update fields based on data
        for field in data:
            setattr(property, field, data[field])

        return property


class SubjectSchema(marshmallow.Schema):
    subject_id = marshmallow.fields.Int()

    study_id = marshmallow.fields.String(validate=lambda s: len(s.strip()) <= 100 and len(s.strip()) > 0)
    generator_url = marshmallow.fields.String(validate=lambda s: len(s) <= 2048)

    @marshmallow.post_load
    def make(self, data):
        if 'subject_id' in data:
            # if we have an subject_id load from db
            subject = db.session.query(models.Subject).filter(models.Subject.subject_id == data['subject_id']).first()
        elif 'study_id' in data:
            # if we have a study_id load from db
            subject = db.session.query(models.Subject).filter(models.Subject.study_id == data['study_id']).first()
            if subject is None:
                # subject does not exist, create a new one
                subject = models.Subject()
        else:
            # else create new object
            subject = models.Subject()

        db.session.commit()

        # update fields based on data
        for field in data:
            setattr(subject, field, data[field])

        return subject


post_experiment = api.model('post-experiment', {
})


@api.route('/experiment/<string:experiment_id>', endpoint='experiment')
class ExperimentGetDeleteEndpoint(Resource):
    @api.response(200, 'OK')
    def get(self, experiment_id):
        schema = ExperimentSchema()

        session = db.session
        try:
            rs = session.query(models.Experiment).filter(and_(models.Experiment.experiment_id == experiment_id, models.Experiment.deleted == None)).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()

            return result, 200
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, experiment_id):
        session = db.session
        try:
            session.query(models.Experiment).filter(models.Experiment.experiment_id == experiment_id).update(
                {models.Experiment.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')

            session.commit()
        except:
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/experiment/bysubject/<string:subject_id>/<string:date>')
class ExperimentPutEndpoint(Resource):
    @api.response(201, 'Experiment successfully created.')
    @api.expect(post_experiment, validate=True)
    def put(self, subject_id, date):
        schema = ExperimentSchema()

        data = request.json
        data['subject_id'] = urllib.parse.unquote_plus(subject_id)
        data['date'] = date
        result = schema.load(request.json)

        print('Result: {}'.format(result))

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        session = db.session
        try:
            session.add(result)
            session.commit()
        except:
            session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201


put_subject = api.model('put-subject', {
    #'study_id': fields.String(required=True,  description='The subject\'s study identifier'),
    'generator_url': fields.String(required=True, descirption='The generator url')
})


@api.route('/subject/bystudyid/<string:study_id>')
class SubjectGetDeleteEndpointByStudyId(Resource):
    @api.response(200, 'OK')
    def get(self, study_id):
        schema = SubjectSchema()

        session = db.session
        try:
            rs = session.query(models.Subject).filter(and_(models.Subject.study_id == study_id, models.Subject.deleted.is_(None))).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()

            return result, 200
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, study_id):
        session = db.session
        try:
            session.query(models.Subject).filter(models.Subject.study_id == study_id).update({models.Subject.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')
            session.commit()
        except:
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/subject/<string:subject_id>')
class SubjectGetDeleteEndpoint(Resource):
    @api.response(200, 'OK')
    def get(self, subject_id):
        schema = SubjectSchema()

        session = db.session
        try:
            rs = session.query(models.Subject).filter(and_(models.Subject.subject_id == subject_id, models.Subject.deleted.is_(None))).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()

            return result, 200
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, subject_id):
        session = db.session
        try:
            session.query(models.Subject).filter(models.Subject.subject_id == subject_id).update({models.Subject.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')
            session.commit()
        except:
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/subject/bystudyid/<string:study_id>')
class SubjectPutEndpoint(Resource):
    @api.response(201, 'Subject successfully created.')
    @api.expect(put_subject, validate=True)
    def put(self, study_id):
        schema = SubjectSchema()

        data = request.json
        data['study_id'] = study_id
        result = schema.load(data)

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        session = db.session
        try:
            session.add(result)
            session.commit()
        except:
            session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201


post_finding = api.model('post-finding', {
    'experiment_id': fields.Integer(required=True, description='The experiment related to this finding'),
    'label_id': fields.Integer(required=True, description='The label related to this finding'),
    'generator_url': fields.String(required=True, description='URL to the generator of this finding'),
    'task_template': fields.String(required=True, description='The task_template related to this experiment'),
})


@api.route('/finding/byexperimentidandtemplateproperty/<string:experiment_id>/<string:template_name>')
class DeleteByExerimentIdEndpoint(Resource):
    @api.response(200, 'OK')
    def delete(self, experiment_id, template_name):
        session = db.session
        try:
            # delete findings themselves
            print(f'Deleting everything for experiment {experiment_id} and template {template_name}')
            targets = session.query(models.Finding).filter(and_(models.Finding.deleted.is_(None),
                                                                models.Finding.task_template == template_name,
                                                                models.Finding.experiment_id == experiment_id))
            # print(f'Need to update {targets.all()}')
            targets.update({models.Finding.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')
            session.commit()

            # now update Properties
            # since not all backends support multiple-table criteria within update we need to do two queries
            subq = session.query(models.Finding.finding_id).filter(models.Finding.deleted.isnot(None)).subquery()

            session.query(models.Property).filter(and_(models.Property.finding_id.in_(subq), models.Property.deleted.is_(None))).update(
                {models.Property.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')
            session.commit()

        except Exception as e:
            print(e)
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/finding/<string:finding_id>')
class FindingGetEndpoint(Resource):
    @api.response(200, 'OK')
    def get(self, finding_id):
        schema = FindingSchema()

        session = db.session
        try:
            rs = session.query(models.Finding).filter(and_(models.Finding.finding_id == finding_id, models.Finding.deleted.is_(None))).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()

            return result, 200
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, finding_id):
        session = db.session
        try:
            session.query(models.Finding).filter(models.Finding.finding_id == finding_id).update(
                {models.Finding.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')

            session.commit()
        except:
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/finding')
class FindingPostEndpoint(Resource):
    @api.response(201, 'Finding successfully created.')
    @api.expect(post_finding, validate=True)
    def post(self):
        schema = FindingSchema()

        result = schema.load(request.json)

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        session = db.session
        try:
            session.add(result)
            session.commit()
        except Exception as e:
            session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201


post_label = api.model('post-label', {
    'label_text': fields.String(required=True, description='The label text'),
})


@api.route('/label/<string:label_id>')
class LabelGetEndpoint(Resource):
    @api.response(200, 'OK')
    def get(self, label_id):
        schema = LabelSchema()

        session = db.session
        try:
            rs = session.query(models.Label).filter(and_(models.Label.label_id == label_id, models.Label.deleted.is_(None))).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()

            return result, 200
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, label_id):
        session = db.session
        try:
            session.query(models.Label).filter(models.Label.label_id == label_id).update(
                {models.Label.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')

            session.commit()
        except:
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/label/bylabeltext/<string:label_text>')
class LabelPutEndpoint(Resource):
    @api.response(201, 'Label successfully created.')
    #@api.expect(post_label, validate=True)
    def put(self, label_text):
        schema = LabelSchema()

        result = schema.load({"label_text": urllib.parse.unquote_plus(label_text)})

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        session = db.session
        try:
            session.add(result)
            session.commit()
        except Exception as e:
            session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201


@api.route('/label')
class LabelGetEndpoint(Resource):
    @api.response(201, 'Label successfully created.')
    @api.expect(post_label, validate=True)
    def post(self):
        schema = LabelSchema()

        result = schema.load(request.json)

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        session = db.session
        try:
            session.add(result)
            session.commit()
        except Exception as e:
            session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201

    @api.response(200, 'OK')
    def get(self):
        schema = LabelSchema(many=True)

        session = db.session
        try:
            rs = session.query(models.Label).all()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()
        except:
            session.rollback()
            return {}, 400

        return result, 200


post_xnatresource = api.model('post-xnatresource', {
    'url': fields.String(required=True,  description='The url to the xnat resource')
})


@api.route('/xnatresource/<string:xnatresource_id>')
class XnatResourceGetEndpoint(Resource):
    @api.response(200, 'OK')
    def get(self, xnatresource_id):
        schema = XnatResourceSchema()

        session = db.session
        try:
            rs = session.query(models.XnatResource).filter(and_(models.XnatResource.xnatresource_id == xnatresource_id, models.XnatResource.deleted.is_(None))).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, xnatresource_id):
        session = db.session
        try:
            session.query(models.XnatResource).filter(models.XnatResource.xnatresource_id == xnatresource_id).update(
                {models.XnatResource.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch')
            session.commit()
        except:
            session.rollback()
            return {}, 500

        return {}, 204


@api.route('/xnatresource/byexperiment/<string:experiment_id>/<string:hash>')
class XnatResourcePutEndpoint(Resource):
    @api.response(201, 'XnatResource successfully created.')
    @api.expect(post_xnatresource, validate=True)
    def post(self, experiment_id, hash):
        schema = XnatResourceSchema()

        data = request.json
        data['experiment_id'] = experiment_id
        data['hash'] = hash

        result = schema.load(data)

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        session = db.session
        try:
            session.add(result)
            session.commit()
        except:
            session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201


put_property = api.model('put-property', {
    'value': fields.String(required=True, description='Serialized / binary data')
})


@api.route('/property/<string:property_id>')
class LabelGetEndpoint(Resource):
    @api.response(200, 'OK')
    def get(self, property_id):
        schema = PropertySchema()

        session = db.session
        try:
            rs = session.query(models.Property).filter(and_(models.Property.property_id == property_id, models.Property.deleted.is_(None))).first()
            if rs is None:
                return {}, 400

            result = schema.dump(rs)
            result = result[0] if len(result) > 0 else {}

            session.commit()
        except:
            session.rollback()
            return {}, 400

        return {}, 200

    @api.response(200, 'OK')
    def delete(self, property_id):
        session = db.session
        try:
            db.session.query(models.Property).filter(models.Property.property_id == property_id).update(
                {models.Property.deleted: datetime.datetime.utcnow()}, synchronize_session='fetch'
            )

            db.session.commit()
        except:
            db.session.rollback()
            return {}, 500

        return {}, 204


@api.route('/property/byfindingid/<string:finding_id>/<string:property_label>')
class FindingPutEndpoint(Resource):
    @api.response(201, 'Property successfully created.')
    @api.expect(put_property, validate=True)
    def put(self, finding_id, property_label):
        schema = PropertySchema()

        data = request.json
        data['finding_id'] = finding_id
        data['label'] = urllib.parse.unquote_plus(property_label)

        result = schema.load(data)

        if len(result[1]) > 0:
            result = result[1]
            return result, 400

        result = result[0]

        try:
            db.session.add(result)
            db.session.commit()
        except Exception as e:
            from pprint import pprint
            pprint(e)
            db.session.rollback()
            return {}, 400

        result = schema.dump(result)
        result = result[0] if len(result) > 0 else {}

        return result, 201


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


@api.route('/views/dbdump')
class DbDumpView(Resource):
    @api.response(200, 'OK')
    def get(self):
        try:
            rs = db.session.query(models.Subject).all()

            db.session.commit()
        except:
            db.session.rollback()
            return {}, 400

        return json.dumps(rs, cls=AlchemyEncoder), 200

# User API
user_list_get = api.model("UserListGet", {
    'users': fields.List(ObjectUrl('api_v1.user', attribute='id'))
})


user_get = api.model("UserGet", {
    'username': fields.String,
    'uri': fields.Url('api_v1.user'),
    'name': fields.String,
    'active': fields.Boolean,
    'email': fields.String,
    'create_time': fields.DateTime,
})


user_put = api.model("UserPut", {
    'username': fields.String,
    'name': fields.String,
    'active': fields.Boolean,
    'email': fields.String,
    'password': fields.String,
})
@api.route('/users', endpoint='users')
class UserListAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('username', type=str, required=True, location='json')
    request_parser.add_argument('password', type=str, required=True, location='json')
    request_parser.add_argument('name', type=str, required=True, location='json')
    request_parser.add_argument('email', type=str, required=True, location='json')
    request_parser.add_argument('active', type=bool, required=False, default=True, location='json')

    @http_auth_required
    @permissions_accepted('user_read_all')
    @api.marshal_with(user_list_get)
    @api.response(200, "Success")
    def get(self):
        users = models.User.query.all()
        return {'users': users}

    @http_auth_required
    @permissions_accepted('user_add')
    @api.marshal_with(user_get)
    @api.expect(user_put)
    @api.response(201, "Created user")
    def post(self):
        args = self.request_parser.parse_args()
        args['password'] = hash_password(args['password'])
        user = user_datastore.create_user(**args)
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user, 201


@api.route('/users/<id>', endpoint='user')
class UserAPI(Resource):
    request_parser = reqparse.RequestParser()
    request_parser.add_argument('username', type=str, required=False, location='json')
    request_parser.add_argument('password', type=str, required=False, location='json')
    request_parser.add_argument('name', type=str, required=False, location='json')
    request_parser.add_argument('email', type=str, required=False, location='json')
    request_parser.add_argument('active', type=bool, required=False, location='json')

    @http_auth_required
    @permissions_accepted('user_read', 'user_read_all')
    @api.marshal_with(user_get)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to get this information")
    @api.response(404, "Could not find user")
    def get(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()

        if not has_permission_any('user_read_all'):
            if user != current_user:
                abort(403, "You are not authorized to get this information")

        if user is None:
            abort(404)

        return user

    @http_auth_required
    @permissions_accepted('user_update_all')
    @api.marshal_with(user_get)
    @api.expect(user_put)
    @api.response(200, "Success")
    @api.response(403, "You are not authorized to perform this operation")
    @api.response(404, "Could not find user")
    def put(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()
        if user is None:
            abort(404)

        args = self.request_parser.parse_args()

        if args['username'] is not None:
            user.username = args['username']

        if args['password'] is not None:
            user.password = args['password']

        if args['name'] is not None:
            user.name = args['name']

        if args['active'] is not None:
            user.active = args['active']

        if args['email'] is not None:
            user.email = args['email']

        db.session.commit()
        db.session.refresh(user)

        return user

    @http_auth_required
    @permissions_accepted('user_delete')
    @api.response(200, "Success")
    @api.response(404, "Could not find user")
    def delete(self, id):
        user = models.User.query.filter(models.User.id == id).one_or_none()

        if user is None:
            abort(404)

        user.active = False
        db.session.commit()

@api.route('/users/<user_id>/roles/<role_id>', endpoint='userrole')
class UserRoleAPI(Resource):
    @auth_required('session', 'basic')
    @permissions_accepted('roles_manage')
    @api.response(200, "Success")
    @api.response(404, "User or Role not found")
    def put(self, user_id, role_id):
        role = get_object_from_arg(role_id, models.Role, models.Role.name)
        user = get_object_from_arg(user_id, models.User, models.User.username)

        if user not in role.users:
            role.users.append(user)
            db.session.commit()
            db.session.refresh(role)

        return {"role": role.id, "user": user.id, "has_role": user in role.users}

    @auth_required('session', 'basic')
    @permissions_accepted('roles_manage')
    @api.response(200, "Success")
    @api.response(404, "User or Role not found")
    def delete(self, user_id, role_id):
        role = get_object_from_arg(role_id, models.Role, models.Role.name)
        user = get_object_from_arg(user_id, models.User, models.User.username)

        user.roles = [x for x in user.roles if x != role]
        db.session.commit()
        db.session.refresh(user)
        db.session.refresh(role)

        return {"role": role.id, "user": user.id, "has_role": user in role.users}
