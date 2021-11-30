from tuxrun.results import Results


def test_returns_0_by_default():
    results = Results()
    assert results.ret() == 0


def gen_test(name, result, suite_name="mytestsuite"):
    return f'{{ "lvl": "results", "msg": {{"definition": "{suite_name}", "case": "{name}", "result": "{result}"}}}}'


def test_returns_0_with_no_failures():
    results = Results()
    results.parse(gen_test("test1", "pass"))
    results.parse(gen_test("test2", "pass"))
    assert results.ret() == 0


def test_returns_1_on_failure():
    results = Results()
    results.parse(gen_test("test1", "pass"))
    results.parse(gen_test("test2", "fail"))
    assert results.ret() == 1


def test_returns_invalid_logs():
    results = Results()
    results.parse("{")
    results.parse('{ "lvl": "results", "msg": {"case": "tux", "result": "pass"}}')


def test_data():
    results = Results()
    results.parse(gen_test("test1", "pass"))
    assert results.data["mytestsuite"]["test1"]["result"] == "pass"
