#  Copyright (c) 2020 Xavier Baró
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
""" Test module for TeSLA CE client creation """


def test_client_creation(base_test_provider_class):
    # Check that client cannot be created without API URL argument
    assert base_test_provider_class is not None

    try:
        base_test_provider_class.get_provider()
    except ModuleNotFoundError as mnfe:
        assert 'PROVIDER_CLASS' in mnfe.__str__()

    provider = base_test_provider_class()



