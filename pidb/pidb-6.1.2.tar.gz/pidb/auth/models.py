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
 
from flask_security.models.fsqla import FsUserMixin
from flask_security.models.fsqla import FsRoleMixin

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseRole(FsRoleMixin):
    """ Base class with the minimally required fields for Role. 
        Please extend this in the app model. """
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class BaseUser(FsUserMixin):
    """ Base class with the minimally required fields for User. 
        Please extend this in the app model. """
    id = db.Column(db.INTEGER, primary_key=True)
    username = db.Column(db.VARCHAR(64), unique=True, nullable=False)
    name = db.Column(db.VARCHAR(64), nullable=False)
    email = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(128), nullable=False)
