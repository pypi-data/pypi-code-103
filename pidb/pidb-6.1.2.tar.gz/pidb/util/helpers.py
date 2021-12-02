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
import os
import yaml
import pprint

from flask_security import SQLAlchemyUserDatastore
from flask_security.utils import hash_password

from .. import models
from .. import exceptions


class LogginMiddleware(object):
    def __init__(self, app):
        self._app = app
    
    def __call__(self, environ, resp):
        errorlog = environ['wsgi.errors']
        pprint.pprint(("REQUEST", environ), stream=errorlog)

        def log_response(status, headers, *args):
            pprint.pprint(("RESPONSE", status, headers), stream=errorlog)
            return resp(status, headers, *args)
        
        return self._app(environ, log_response)


def get_object_from_arg(id, model, model_name=None, skip_id=False, allow_none=False):
    data = None

    if isinstance(id, model):
        return id

    if id is not None:
        # If we have a URI/path we just want the last part
        if isinstance(id, str) and '/' in id:
            id = id.rsplit('/', 1)[1]

        # For id try to cast to an int
        if not skip_id:
            try:
                id = int(id)
            except (TypeError, ValueError) as e:
                pass

        if isinstance(id, int):
            data = model.query.filter(model.id == id).one_or_none()
        elif model_name is not None:
            data = model.query.filter(model_name == id).one_or_none()

    if data is None and not allow_none:
        raise exceptions.CouldNotFindResourceError(id, model)

    return data


def load_config_file(app, file_path, silent=False):
    file_path = str(file_path)

    with app.app_context():
        db = models.db

        user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        if not os.path.isfile(file_path):
            db.session.rollback()
            raise ValueError(f"The file ({file_path}) does not exist")

        with open(file_path) as fh:
            config = yaml.safe_load(fh)

        if 'roles' in config:
            if not silent:
                print("\n Adding Roles:")
            roles = {}
            for role in config["roles"]:
                if models.Role.query.filter(models.Role.name == role['name']).count() == 0:
                    roles[role['name']] = user_datastore.create_role(**role)
                    if not silent:
                        print(f"{roles[role['name']]} {role}")
                else:
                    print(f"[WARNING] Skipping Role {role['name']}, already exists!")
            db.session.commit()

        if 'users' in config:
            if not silent:
                print("\nAdding users:")
            for user in config['users']:
                # Make sure user is confirmed
                user['confirmed_at'] = datetime.datetime.now()
                if models.User.query.filter((models.User.username == user['username']) | (models.User.email == user['email'])).count() == 0:
                    user['password'] = hash_password(user['password'])
                    db_user = user_datastore.create_user(**user)
                    if not silent:
                        print(f"Adding {db_user}")
                else:
                    print(f"[WARNING] Skipping User {user['username']} / {user['email']}, user and/or username already used!")
            db.session.commit()

        if not silent:
            print("\nCommitting to the database ...")
        db.session.commit()
        if not silent:
            print("[ DONE ]")

