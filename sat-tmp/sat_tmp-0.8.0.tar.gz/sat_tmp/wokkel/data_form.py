# -*- coding: utf-8 -*-
# -*- test-case-name: wokkel.test.test_rsm -*-
#
# Series of Wokkel patches used by SàT
# Copyright (C) 2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from wokkel import data_form
from twisted.words.xish import domish

NS_XML_ELEMENT = "urn:xmpp:xml-element"


class Field(data_form.Field):
    """Field class adding implementation for XML Element"""


    def __init__(self, fieldType='text-single', var=None, value=None,
                       values=None, options=None, label=None, desc=None,
                       required=False, ext_type=None):
        """
        @param ext_type(None, unicode): extended type, can be:
            - xml: field is an XML Element
            - None: field is a base (XEP-0004) type
        """

        super(Field, self).__init__(fieldType, var, value, values, options, label, desc,
                                    required)
        self.ext_type = ext_type

    def typeCheck(self):
        if self.ext_type is not None:
            # we use an extended type
            if self.fieldType not in (None, 'hidden'):
                raise ValueError('Invalid main type for a extended type field')
            if len(self.values) != 1:
                raise ValueError('extended type must have one and only one value')
            if self.options:
                raise ValueError('options must not be set for extented type')
            if self.ext_type == 'xml':
                if not isinstance(self.value, domish.Element):
                    raise ValueError('invalid value, a domish.Element is expected')
            else:
                raise ValueError(
                    'Unknown extended type: {ext_type}'.format(ext_type=self.ext_type))
        return super(Field, self).typeCheck()

    def toElement(self, asForm=False):
        if self.ext_type is None:
            return super(Field, self).toElement(asForm)
        else:
            self.typeCheck()
            field_elt = domish.Element((data_form.NS_X_DATA, 'field'))
            if self.fieldType:
                field_elt['type'] = self.fieldType

            if self.var is not None:
                field_elt['var'] = self.var

            wrapper_elt = field_elt.addElement((NS_XML_ELEMENT, 'wrapper'))
            wrapper_elt.addChild(self.value)

            if asForm:
                if self.label is not None:
                    field_elt['label'] = self.label

                if self.desc is not None:
                    field_elt.addElement('desc', content=self.desc)

                if self.required:
                    field_elt.addElement('required')

            return field_elt

    @staticmethod
    def fromElement(element):
        field = super(Field, Field).fromElement(element)
        if element.wrapper and element.wrapper.uri == NS_XML_ELEMENT:
            field.ext_type = "xml"
            field.value = element.wrapper.firstChildElement()
        return field


def install():
    data_form.Field = Field
