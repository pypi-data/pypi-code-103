#  Copyright (c) 2021 Roger Muñoz
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" TeSLA CE Keystroke utility module """
import base64
from base64 import binascii
import json
from json.decoder import JSONDecodeError
from tesla_ce_provider import message



def get_sample_ks(sample):
    """
        Get Keystroke data features from sample

        :param sample: Sample structure
        :type sample: tesla_ce_provider.models.base.Sample | tesla_provider.models.base.Request
        :return: Image
        :rtype: np.Array
    """
    try:
        data = sample.data.split(',')[1]
    except AttributeError:
        return None
    except IndexError:
        data = sample.data

    try:
        datab64 = base64.b64decode(data)
    except binascii.Error:
        return None

    try:
        ks_array = json.loads(datab64)
    except (TypeError, JSONDecodeError):
        return None

    for ks_line in ks_array:
        if 'features' not in ks_line.keys():
            return None

    return ks_array


def check_sample_ks(sample, accepted_mimetypes=None):
    """
        Check sample information
        :param sample: Sample structure
        :type sample: tesla_ce_provider.models.base.Sample | tesla_provider.models.base.Request
        :param accepted_mimetypes: Accepted mimetype values
        :type accepted_mimetypes: list
        :return: An object with the image and mimetype or the found errors
        :rtype: dict
    """
    # Check mimetype
    mimetype = None
    try:
        sample_mimetype = sample.data.split(',')[0].split(';')[0].split(':')[1]
        if len(sample_mimetype.strip()) == 0:
            sample_mimetype = None
    except IndexError:
        sample_mimetype = None
    if sample.mime_type is not None:
        mimetype = sample.mime_type
    if sample_mimetype is not None and mimetype is not None and sample_mimetype != mimetype:
        return {
            'valid': False,
            'msg': "Mimetype in sample data differs from sample mimetype",
            'code': message.Provider.PROVIDER_INVALID_MIMETYPE.value,
            'image': None
        }
    if mimetype is None:
        mimetype = sample_mimetype
    if mimetype is None:
        return {
            'valid': False,
            'msg': "Missing mimetype.",
            'code': message.Provider.PROVIDER_MISSING_MIMETYPE.value,
            'image': None
        }
    if mimetype not in accepted_mimetypes:
        return {
            'valid': False,
            'msg': f"Invalid mimetype. Accepted types are: [{', '.join(accepted_mimetypes)}]",
            'code': message.Provider.PROVIDER_INVALID_MIMETYPE.value,
            'image': None
        }

    ks_data = get_sample_ks(sample)
    if ks_data is None:
        return {
            'valid': False,
            'msg': "Invalid image format in sample data.",
            'code': message.Provider.PROVIDER_INVALID_SAMPLE_DATA.value,
            'image': None
        }

    return {
        'valid': True,
        'mimetype': mimetype,
        'ks_data': ks_data
    }
