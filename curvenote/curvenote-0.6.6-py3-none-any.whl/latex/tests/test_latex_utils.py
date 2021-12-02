import re

import pytest

from curvenote.client import API_URL
from curvenote.latex import utils
from curvenote.latex.utils.index import LocalMarker


def test_block_hash_to_url():
    block_hash = "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E"
    url = utils.block_hash_to_api_url(API_URL, block_hash)
    assert url == f"{API_URL}/blocks/VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E"


def test_unpinned_block_hash_to_url():
    block_hash = "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1"
    url = utils.block_hash_to_api_url(API_URL, block_hash)
    assert (
        url == f"{API_URL}/blocks/VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/versions/1"
    )


def test_unpinned_oxa_path_to_url():
    oxa_path = "oxa:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E"
    url = utils.oxa_path_to_api_url(API_URL, oxa_path)
    assert url == f"{API_URL}/blocks/VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E"


def test_oxa_path_to_url():
    oxa_path = "oxa:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E.1"
    url = utils.oxa_path_to_api_url(API_URL, oxa_path)
    assert (
        url == f"{API_URL}/blocks/VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/versions/1"
    )


def test_find_no_images_in_tex():
    content = """
        lorem ipsum anythingim
        \\begin{center}
        \\somthing{abc}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """
    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )
    assert summary.content == content
    assert summary.remote_paths == []
    assert summary.local_paths == []


def test_find_one_image_in_bigger_tex_block__block_path():
    content = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    updated = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )

    assert summary.content == updated
    assert summary.remote_paths == ["block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1"]
    assert summary.local_paths == ["images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1"]


def test_find_one_image_in_bigger_tex_block__oxa_path():
    content = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{oxa:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E.1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    updated = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E.1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )

    assert summary.content == updated
    assert summary.remote_paths == ["oxa:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E.1"]
    assert summary.local_paths == ["images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E.1"]


def test_find_two_images_in_tex__block_path():
    content = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
        \\includegraphics[width=0.7\\linewidth]{block:aaaaabbbbbcccccddddd/xxxxxyyyyyccccc11111/9}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    updated = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
        \\includegraphics[width=0.7\\linewidth]{images/aaaaabbbbbcccccddddd_xxxxxyyyyyccccc11111_9}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )

    assert summary.content == updated
    assert len(summary.remote_paths) == 2
    assert len(summary.local_paths) == 2

    assert summary.remote_paths == [
        "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1",
        "block:aaaaabbbbbcccccddddd/xxxxxyyyyyccccc11111/9",
    ]

    assert summary.local_paths == [
        "images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1",
        "images/aaaaabbbbbcccccddddd_xxxxxyyyyyccccc11111_9",
    ]


def test_find_two_images_in_tex__mixed_paths():
    content = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
        \\includegraphics[width=0.7\\linewidth]{oxa:aaaaabbbbbcccccddddd/xxxxxyyyyyccccc11111.9}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    updated = """
        lorem ipsum anythingim
        \\subsection*{Heading 3}
        \\begin{center}
        \\includegraphics[width=0.7\\linewidth]{images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1}
        \\end{center}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
        \\includegraphics[width=0.7\\linewidth]{images/aaaaabbbbbcccccddddd_xxxxxyyyyyccccc11111.9}
        \\subsection*{Heading 3}
        lorem ipsum anythingim
    """

    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )

    assert summary.content == updated
    assert len(summary.remote_paths) == 2
    assert len(summary.local_paths) == 2

    assert summary.remote_paths == [
        "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1",
        "oxa:aaaaabbbbbcccccddddd/xxxxxyyyyyccccc11111.9",
    ]

    assert summary.local_paths == [
        "images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1",
        "images/aaaaabbbbbcccccddddd_xxxxxyyyyyccccc11111.9",
    ]


def test_patch_one_image_in_tex_block__block_path():
    content = """
        abc
        \\includegraphics[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1}
        xyz
    """

    updated = """
        abc
        \\includegraphics[width=0.7\\linewidth]{images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1}
        xyz
    """
    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )

    assert summary.content == updated
    assert summary.remote_paths == ["block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1"]
    assert summary.local_paths == ["images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E_1"]


def test_patch_one_image_in_tex_block__oxa_path():
    content = """
        abc
        \\includegraphics[width=0.7\\linewidth]{oxa:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E.1}
        xyz
    """

    updated = """
        abc
        \\includegraphics[width=0.7\\linewidth]{images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E.1}
        xyz
    """
    summary = utils.patch_local_images_from_tex_block(
        [utils.INLINE_IMAGE_BLOCK_REGEX, utils.INLINE_IMAGE_OXA_REGEX], content
    )

    assert summary.content == updated
    assert summary.remote_paths == ["oxa:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E.1"]
    assert summary.local_paths == ["images/VYoEVcBJZ5lZ0MW7cYh7_UtUKWdGQQquIXAxWmN9E.1"]


def test_output_image_regex_is_matched():
    content = (
        "abc"
        "\\includegraphics[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1-output-3}"
        "xyz"
    )

    match = re.search(utils.OUTPUT_IMAGE_BLOCK_REGEX, content)
    assert match is not None
    assert match[0] == content
    assert match[1] == "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1-output-3"


def test_output_image_regex_not_matched():
    content = "\\includegraphics[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1}"

    match = re.search(utils.OUTPUT_IMAGE_BLOCK_REGEX, content)
    assert match is None


def test_output_svg_regex_is_matched():
    content = (
        "abc"
        "\\includesvg[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1-output-3}"
        "xyz"
    )

    match = re.search(utils.OUTPUT_SVG_BLOCK_REGEX, content)
    assert match is not None
    assert match[0] == content
    assert match[1] == "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1-output-3"


def test_output_svg_regex_not_matched():
    content = "\\includesvg[width=0.7\\linewidth]{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E/1}"

    match = re.search(utils.OUTPUT_SVG_BLOCK_REGEX, content)
    assert match is None


def test_cite_regex():
    content = r"""single citation in a block \citep{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E}
two copies of the same citation (\cite{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9F}) within the same \citet{block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9G} block
    """
    match = re.findall(utils.INLINE_CITATION_BLOCK_REGEX, content)
    assert len(match) == 3
    assert match[0] == "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9E"
    assert match[1] == "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9F"
    assert match[2] == "block:VYoEVcBJZ5lZ0MW7cYh7/UtUKWdGQQquIXAxWmN9G"


def test_figure_regex():
    content = r"""\\begin{figure}[h]
        \\centering
        \\includegraphics[width=0.7\linewidth]{block:V1qG9ZexyVrBGNsaz5Rh/OZqqWnecItn4CkZPDCy6/1}
        \\caption{block:V1qG9ZexyVrBGNsaz5Rh/OZqqWnecItn4CkZPDCy6/1.caption}
        \\label{some-ting-1}
    \\end{center}"""

    match = re.findall(utils.CAPTION_COMMAND_BLOCK_REGEX, content, flags=re.S)
    assert match
    assert len(match) == 1
    assert match[0] == "block:V1qG9ZexyVrBGNsaz5Rh/OZqqWnecItn4CkZPDCy6/1.caption"


def test_figure_label():
    content = r"""\\begin{figure}[h]
        \\centering
        \\includegraphics[width=0.7\linewidth]{block:V1qG9ZexyVrBGNsaz5Rh/OZqqWnecItn4CkZPDCy6/1}
        \\caption{block:V1qG9ZexyVrBGNsaz5Rh/OZqqWnecItn4CkZPDCy6/1.caption}
        \\label{some-ting-1}
    \\end{center}"""

    match = re.findall(utils.LABEL_COMMAND_REGEX, content, flags=re.S)
    assert match
    assert len(match) == 1
    assert match[0] == "some-ting-1"


def test_parse_cite_tag_from_version():
    local_tag, plain_tag = utils.parse_cite_tag_from_bibtex(
        """@article{Cockett2016Pixels,
        author = {Cockett, Rowan and Heagy, Lindsey J. and Oldenburg, Douglas W.},
        journal = {The Leading Edge},
        number = {8},
        year = {2016},
        month = {8},
        pages = {703--706},
        title = {Pixels and their neighbors: Finite volume},"""
    )
    assert "Cockett2016Pixels" in plain_tag
    assert re.match(r"^Cockett2016Pixels_[0-9a-zA-Z]+", local_tag)


def test_find_groups_in_content():
    pass


@pytest.fixture(
    params=[
        ("", ""),
        ("hello world", "hello world"),
        ("he\\ llo world", r"he{\textbackslash}~llo world"),
        ("he\\llo world", r"he{\textbackslash}llo world"),
        ("he\\llo wor\\ld", r"he{\textbackslash}llo wor{\textbackslash}ld"),
        ("hello~world", r"hello{\textasciitilde}world"),
        ("hello&world", r"hello\&world"),
        ("hello%world", r"hello\%world"),
        ("hello$world", r"hello\$world"),
        ("hello#world", r"hello\#world"),
        ("hello_world", r"hello\_world"),
        ("hello{world", r"hello\{world"),
        ("hello}world", r"hello\}world"),
        ("hello^world", r"hello\^world"),
    ],
    name="to_escape",
)
def _to_escape(request):
    return request.param


def test_escape_latex(to_escape):
    example, escaped = to_escape
    assert utils.escape_latex(example) == escaped


def test_local_markers_can_be_used_in_set_based_on_marker():
    deduped = list(
        set(
            [
                LocalMarker(
                    marker="a", local_path="qwe", remote_path="daa", content="ghj"
                ),
                LocalMarker(
                    marker="b", local_path="qwsde", remote_path="da6a", content="g4hj"
                ),
                LocalMarker(
                    marker="a", local_path="qwhe", remote_path="da8a", content="gh32j"
                ),
            ]
        )
    )

    assert len(deduped) == 2
    assert deduped[0].marker == "a" or deduped[0].marker == "b"
    assert deduped[1].marker == "a" or deduped[1].marker == "b"
