import pytest

from markdown_helper import MarkdownHelper, MarkdownLine


@pytest.fixture
def mdh():
    return MarkdownHelper.__new__(MarkdownHelper)


@pytest.fixture
def mdh_simple(mdh):
    mdh.raw_content = ['zero', '# one', '## two']
    return mdh


def test_should_get_header_level_from_line(mdh):
    assert mdh._get_header_level('') == 0
    assert mdh._get_header_level('# adsf') == 1
    assert mdh._get_header_level('## adsf') == 2
    assert mdh._get_header_level('# #') == 1
    assert mdh._get_header_level(' ##') == 0


def test_calculate_new_index(mdh):
    assert mdh._get_markdown_line([], 'test')[0] == []

    assert mdh._get_markdown_line([], '# test')[0] == [1]
    assert mdh._get_markdown_line([2], '## test')[0] == [2, 1]

    assert mdh._get_markdown_line([1], '# test')[0] == [2]
    assert mdh._get_markdown_line([1, 2], '## test')[0] == [1, 3]

    assert mdh._get_markdown_line([1, 2], '# test')[0] == [2]
    assert mdh._get_markdown_line([1, 2, 3], '## test')[0] == [1, 3]


def test_calculate_new_line(mdh):
    assert mdh._get_markdown_line([], 'test')[1] == MarkdownLine(index=[], line='test')
    assert mdh._get_markdown_line([], '# test')[1] == MarkdownLine(index=[1], line='# test')
    assert mdh._get_markdown_line([1, 2, 3], '## test')[1] == MarkdownLine(index=[1, 3], line='## test')


def test_conversion(mdh_simple):
    assert mdh_simple._convert_to_mdlines(mdh_simple.raw_content) == [MarkdownLine(index=[], line='zero'),
                                                                      MarkdownLine(index=[1], line='# one'),
                                                                      MarkdownLine(index=[1, 1], line='## two')]
