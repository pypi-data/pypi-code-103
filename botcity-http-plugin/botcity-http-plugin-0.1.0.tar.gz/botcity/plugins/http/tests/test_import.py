def test_package_import():
    import botcity.plugins.http as plugin
    assert plugin.__file__ != ""
