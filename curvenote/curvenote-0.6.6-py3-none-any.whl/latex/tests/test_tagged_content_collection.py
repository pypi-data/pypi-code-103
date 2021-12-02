from curvenote.latex.TaggedContentCollection import TaggedContentCollection


def test_init():
    c = TaggedContentCollection()
    assert list(c.keys()) == []


def test_add():
    c = TaggedContentCollection()

    c.add("a", "b")
    assert c["a"] == "b\n"

    c.add("a", "c")
    assert c["a"] == "b\n\nc\n"

    c.add("p", "plain", True)
    assert c["p"] == "plain"

    c.add("p", "text", True)
    assert c["p"] == "plain text"

def test_merge():
    c1 = TaggedContentCollection()
    c2 = TaggedContentCollection()

    c1.add("a", "b")
    c1.add("b", "c")

    c2.add("a", "d")
    c2.add("c", "e")

    c1.merge(c2)

    assert c1["a"] == "b\n\nd\n"
    assert c1["b"] == "c\n"
    assert c1["c"] == "e\n"

def test_merge_with_plain():
    c1 = TaggedContentCollection()
    c2 = TaggedContentCollection()

    c1.add("a", "b", plain=True)
    c1.add("b", "c")

    c2.add("a", "d", plain=True)
    c2.add("c", "e")

    c1.merge(c2)

    assert c1["a"] == "b d"
    assert c1["b"] == "c\n"
    assert c1["c"] == "e\n"
