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

from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from .auth.models import BaseUser
from .auth.models import BaseRole

db = SQLAlchemy()


class Experiment(db.Model):
    __tablename__ = 'experiment'

    experiment_id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.DateTime)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    subject = db.relationship("Subject", back_populates="experiments")

    xnat_resources = db.relationship("XnatResource", back_populates="experiment")

    findings = db.relationship("Finding", back_populates="experiment")

    inserted = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    deleted = db.Column(db.DateTime, default=None)

    __table_args__ = (db.UniqueConstraint('date', 'subject_id', name='_date_subject_uc'),)


class Finding(db.Model):
    __tablename__ = 'finding'

    finding_id = db.Column(db.Integer, primary_key=True)

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.experiment_id'), nullable=False)
    experiment = db.relationship("Experiment", back_populates="findings")

    task_template = db.Column(db.Text(length=255))  # <-- finding has a template?

    label_id = db.Column(db.Integer, db.ForeignKey('label.label_id'), nullable=False)
    label = db.relationship("Label", back_populates="findings")

    properties = db.relationship("Property", back_populates="finding")

    generator_url = db.Column(db.String(length=512), nullable=False)

    inserted = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    deleted = db.Column(db.DateTime, default=None)


class Gender(Enum):
    MALE = 0
    FEMALE = 1
    UNKNOWN = 2


class Label(db.Model):
    __tablename__ = 'label'

    label_id = db.Column(db.Integer, primary_key=True)

    findings = db.relationship("Finding", back_populates="label")

    label_text = db.Column(db.String(length=255), unique=True)

    inserted = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    deleted = db.Column(db.DateTime, default=None)


class Property(db.Model):
    __tablename__ = 'property'

    property_id = db.Column(db.Integer, primary_key=True)

    finding_id = db.Column(db.Integer, db.ForeignKey('finding.finding_id'))
    finding = db.relationship("Finding", back_populates="properties")

    label = db.Column(db.String(length=64))
    value = db.Column(db.Text(length=65535))

    inserted = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    deleted = db.Column(db.DateTime, default=None)


class Subject(db.Model):
    __tablename__ = 'subject'

    subject_id = db.Column(db.Integer, primary_key=True)

    experiments = db.relationship("Experiment", back_populates="subject")

    #gender = db.Column(Enum(Gender), default=Gender.UNKNOWN)
    study_id = db.Column(db.String(100), unique=True, nullable=False)
    generator_url = db.Column(db.Text())

    inserted = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    deleted = db.Column(db.DateTime, default=None)


class XnatResource(db.Model):
    __tablename__ = 'xnat_resource'

    xnatresource_id = db.Column(db.Integer, primary_key=True)

    experiment_id = db.Column(db.Integer, db.ForeignKey('experiment.experiment_id'))
    experiment = db.relationship("Experiment", back_populates="xnat_resources")

    url = db.Column(db.Text())
    hash = db.Column(db.String(32)) # 32 chars for MD5

    inserted = db.Column(db.DateTime, default=func.now())
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    deleted = db.Column(db.DateTime, default=None)


# User and Role models used for authentication and authorization
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id', name="fk_roles_users_user_id_user")),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id', name="fk_roles_users_role_id_role")))


class Role(db.Model, BaseRole):
    """ This implements the BaseRole from the .auth.models module.
    In this specific case, the BaseRole is sufficient. """
    __tablename__ = 'role'
    pass


class User(db.Model, BaseUser):
    __tablename__ = 'user'
    create_time = db.Column(db.DateTime(timezone=True), default=func.now())
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.username} ({self.name})>'
