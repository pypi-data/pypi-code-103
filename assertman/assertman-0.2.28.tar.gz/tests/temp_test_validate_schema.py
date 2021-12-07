from assertman.cerberus_wrapper.validators import SkyrimValidator

result = {
    "id": 78866,
    "status": "active",
    "uuu": None,
    "age_levels": {"new": 10, "medium": 20, "old": 30, "inner_dict": {"a": 1, "b":"2"}},
    "actors": ["TwoActor", "TwoActor", "TwoActor"],
    "assets": [
        {"name": "3d", "price": 750, "is_old": "yes",
        "target": {"url": "http://mos"}, "mrf": ["v_mos", "v_ct"]},
        {"name": "hd", "price": 500, "is_old": "yes",
        "target": {"url": "http://mos"}, "mrf": ["v_mos", "v_ct"]},
        {"name": "sd", "price": 250, "is_old": "yes",
        "target": {"url": "http://mos"}, "mrf": ["v_mos", "v_ct"]}
    ],
    "wins": [],
    "is_favorite": True
}


def validate(schema, document):
    v = SkyrimValidator(schema, allow_unknown=True, require_all=True)
    r = v.validate(document)
    if r is False:
        assert False, v.errors


def test_equal_to():
    schema = {
        'id': {
            'type': 'integer',
            'equal_to': 78866,
        },
    }

    validate(schema, result)


def test_has_key():
    schema = {
        # 'type': 'dict',
        'has_key': {'type': 'string', 'regex': '[a-z]+'}
    }
    result = {'key': 'value'}
    validate(schema, result)

