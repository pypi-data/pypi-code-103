import itertools
import json
import math
from datetime import datetime
from unittest import TestCase

import bson
import pytz
from bson import string_type
from bson.json_util import DatetimeRepresentation, JSONOptions

from bson_extra import BsonExtra, bson_extra


class TestBsonExtra(TestCase):
    def setUp(self):
        super(TestBsonExtra, self).setUp()
        # The timezone to use for timezone aware tests
        self.zone = "America/New_York"

    def _json_options(self):
        """
        Builds all possible combinations of options to use for loads and dumps
        :return:
        """
        json_options = [
            (None, None),
        ]
        datetime_representations = []
        tz_aware = [True, False]

        for attr in dir(DatetimeRepresentation):
            # Build a list of all possible datetime representations
            if attr.startswith("_"):
                continue
            datetime_representations.append(
                getattr(DatetimeRepresentation, attr)
            )

        perms = itertools.product(datetime_representations, tz_aware)
        for _datetime_representation, _tz_aware in perms:
            # Create JSONOptions for all permutations of datetime representation
            # and tz_aware, handles each of these being present in loads
            # and dumps, or a combination of them
            _json_options = JSONOptions(
                tz_aware=_tz_aware,
                datetime_representation=_datetime_representation,
            )
            json_options.append((_json_options, None))
            json_options.append((_json_options, _json_options))
            json_options.append((None, _json_options))
        for _json_option in json_options:
            yield _json_option

    def _do_test(self, dt, _dump_options=None, _load_options=None):
        """
        The base test that all test cases should test against
        :param dt: The datetime that is being tested
        :type dt:datetime.datetime
        :param _dump_options:The JSONOptions to use for dumping the data
        :type _dump_options:dict
        :param _load_options:The JSONOptions to use for loading the data
        :type _load_options:dict
        """
        is_aware = False
        zone = None
        if dt.tzinfo is not None:
            is_aware = True
            zone = dt.tzinfo.zone

        dump_options = {}
        load_options = {}
        if _dump_options:
            dump_options = {"json_options": _dump_options}
        if _load_options:
            load_options = {"json_options": _load_options}

        dumped_data = bson_extra.dumps(dt, **dump_options)
        offset = None

        if is_aware and isinstance(
            json.loads(dumped_data)["$date"], string_type
        ):
            # the data was dumped as a ISO 8601 representation
            millis = int(dt.microsecond / 1000)
            fracsecs = ".%03d" % (millis,) if millis else ""
            dumped_date = "%s%s" % (dt.strftime("%Y-%m-%dT%H:%M:%S"), fracsecs)
        else:
            # the data was dumped as a epoch timestamp
            dumped_date = bson._datetime_to_millis(dt)
            if is_aware:
                # It's a TZ aware datetime - ensure the offset is set
                offset = {"total_seconds": dt.utcoffset().total_seconds()}

            if _dump_options and (
                _dump_options.datetime_representation
                == DatetimeRepresentation.NUMBERLONG
                or _dump_options.datetime_representation
                == DatetimeRepresentation.ISO8601
            ):
                # $numberLong format gets saved slightly differently.
                # ISO8601 TZ naive timestamps also get saved as $numberLong
                dumped_date = {"$numberLong": str(dumped_date)}

        expected_data = json.dumps(
            {"$date": dumped_date, "$zone": zone, "$offset": offset}
        )

        assert dumped_data == expected_data

        loaded_data = bson_extra.loads(dumped_data, **load_options)

        milliseconds = math.floor(dt.microsecond / 1000) * 1000

        assert loaded_data == dt.replace(microsecond=milliseconds)

    def test_tz_aware_dst(self):
        """
        Tests dumping and loading a timezone aware datetime that has DST
        for all possible DatetimeRepresentations and tz_aware_values
        """
        dt = datetime(2020, 6, 20, 12, 0, 0)
        dt = dt.astimezone(pytz.timezone(self.zone))
        for _dump_options, _load_options in self._json_options():
            self._do_test(
                dt=dt,
                _dump_options=_dump_options,
                _load_options=_load_options,
            )

    def test_tz_naive_dst(self):
        """
        Tests dumping and loading a timezone naive datetime that has DST
        for all possible DatetimeRepresentations and tz_aware_values
        """
        dt = datetime(2020, 6, 20, 12, 0, 0)
        for _dump_options, _load_options in self._json_options():
            self._do_test(
                dt=dt,
                _dump_options=_dump_options,
                _load_options=_load_options,
            )

    def test_tz_aware_no_dst(self):
        """
        Tests dumping and loading a timezone aware datetime that has no DST
        for all possible DatetimeRepresentations and tz_aware_values
        """
        dt = datetime(2020, 12, 20, 12, 0, 0)
        dt = dt.astimezone(pytz.timezone(self.zone))
        for _dump_options, _load_options in self._json_options():
            self._do_test(
                dt=dt,
                _dump_options=_dump_options,
                _load_options=_load_options,
            )

    def test_tz_naive_no_dst(self):
        """
        Tests dumping and loading a timezone naive datetime that has no DST
        for all possible DatetimeRepresentations and tz_aware_values
        """
        dt = datetime(2020, 12, 20, 12, 0, 0)
        for _dump_options, _load_options in self._json_options():
            self._do_test(
                dt=dt,
                _dump_options=_dump_options,
                _load_options=_load_options,
            )

    def test_custom_type(self):
        """
        Tests that a user can subclass BsonExtra and hook into the class to
        be able to save custom types as json
        """
        value = 100

        class CustomBsonExtra(BsonExtra):
            def dump_object_hook(self, obj, json_options):
                if isinstance(obj, int):
                    result = {"$integer": obj}
                else:
                    result = super(CustomBsonExtra, self).dump_object_hook(
                        obj, json_options
                    )
                return result

            def load_object_hook(self, dct, *args, **kwargs):
                result = super(CustomBsonExtra, self).load_object_hook(
                    dct, *args, **kwargs
                )
                if "$integer" in dct:
                    return int(dct["$integer"])
                return result

        # The data as it would be dumped by the base bson_extra class
        original_dumped_data = bson_extra.dumps(value)

        custom_bson_extra = CustomBsonExtra()
        dumped_data = custom_bson_extra.dumps(value)

        # Our custom class should handle integers as ints (by default integers
        # are handled as strings)
        assert original_dumped_data == str(value)
        assert dumped_data == json.dumps({"$integer": value})

        original_loaded_data = bson_extra.loads(original_dumped_data)
        loaded_data = custom_bson_extra.loads(dumped_data)

        # Ensures that the types is the same as it would have been originally
        assert original_loaded_data == value
        assert loaded_data == value
        assert original_loaded_data == loaded_data
