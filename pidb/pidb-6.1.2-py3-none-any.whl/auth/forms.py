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

from flask_security.forms import LoginForm, RegisterForm, unique_identity_attribute

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class AuthLoginForm(LoginForm):
    email = StringField('Email/Username', validators=[DataRequired()])


class AuthRegisterForm(RegisterForm):
    username = StringField('Username', validators=[DataRequired(), unique_identity_attribute])
    name = StringField('Name', validators=[DataRequired()])
