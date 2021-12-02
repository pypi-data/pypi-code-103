import pytest
from jtex.options import (
    AsideSchemaOption,
    SchemaOptionDefs,
    StringSchemaOption,
)


def test_empty_option():
    opts = StringSchemaOption()
    with pytest.raises(ValueError) as err:
        opts.get()
    assert "No default option set" in str(err)


def test_unknown_option():
    opts = StringSchemaOption()
    with pytest.raises(ValueError) as err:
        opts.get("something")
    assert "Unknown option: something" in str(err)


def test_add_option():
    opts = StringSchemaOption()
    opts.add("a", SchemaOptionDefs(["a"], ["b"], ["c"]))
    assert opts.get("a").passopts == ["a"]
    assert opts.get("a").packages == ["b"]
    assert opts.get("a").setup == ["c"]


def test_default_option():
    opts = StringSchemaOption()
    opts.add("a", SchemaOptionDefs(["a"], ["b"], ["c"]))
    opts.default = "a"
    assert opts.get().passopts == ["a"]
    assert opts.get().packages == ["b"]
    assert opts.get().setup == ["c"]


def test_names():
    opts = StringSchemaOption()
    opts.add("a", SchemaOptionDefs())
    opts.add("b", SchemaOptionDefs())
    assert opts.names() == ["a", "b"]


def test_aside_options():
    aside = AsideSchemaOption()

    assert aside.default == "marginpar"
    assert "marginpar" in aside.names()
    assert "framed" in aside.names()
    assert "mdframed" in aside.names()
    assert "callout" in aside.names()
    assert "aside.def" in aside.names()
