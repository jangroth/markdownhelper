import pytest

from markdown_helper import MarkdownHelper


@pytest.fixture
def markdown_helper():
    result = MarkdownHelper.__new__(MarkdownHelper)
    return result


def test_should_get_header_level_from_line(markdown_helper):
    assert markdown_helper._get_header_level('') == 0
    assert markdown_helper._get_header_level('# adsf') == 1
    assert markdown_helper._get_header_level('## adsf') == 2
    assert markdown_helper._get_header_level('# #') == 1
    assert markdown_helper._get_header_level(' ##') == 0


def test_calculate_new_index(markdown_helper):
    assert markdown_helper._get_markdown_line([], 'asdf')[0] == []

    assert markdown_helper._get_markdown_line([], '# asdf')[0] == [1]
    assert markdown_helper._get_markdown_line([2], '## asdf')[0] == [2, 1]

    assert markdown_helper._get_markdown_line([1], '# asdf')[0] == [2]
    assert markdown_helper._get_markdown_line([1, 2], '## asdf')[0] == [1, 3]

    assert markdown_helper._get_markdown_line([1, 2], '# asdf')[0] == [2]
    assert markdown_helper._get_markdown_line([1, 2, 3], '## asdf')[0] == [1, 3]
