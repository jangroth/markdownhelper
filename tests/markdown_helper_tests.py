import pytest

from markdown_helper import MarkdownLine, MarkdownHelper


@pytest.fixture
def mdl():
    return MarkdownLine.__new__(MarkdownLine)


@pytest.fixture
def mdh():
    return MarkdownHelper.__new__(MarkdownHelper)


def test_should_get_header_level_from_line(mdl):
    assert mdl._get_header_level('') == 0
    assert mdl._get_header_level('# adsf') == 1
    assert mdl._get_header_level('## adsf') == 2
    assert mdl._get_header_level('# #') == 1
    assert mdl._get_header_level(' ##') == 0


def test_calculate_new_index(mdl):
    assert mdl._generate_index([], 'test') == []
    assert mdl._generate_index([1], 'test') == [1]

    assert mdl._generate_index([], '# test') == [1]
    assert mdl._generate_index([2], '## test') == [2, 1]

    assert mdl._generate_index([1], '# test') == [2]
    assert mdl._generate_index([1, 2], '## test') == [1, 3]

    assert mdl._generate_index([1, 2], '# test') == [2]
    assert mdl._generate_index([1, 2, 3], '## test') == [1, 3]


def test_parse_file(mdh):
    mdlines = mdh._convert_to_mdlines(['one', '# two', 'three', '# four'])

    assert [(mdline.index, mdline.line) for mdline in mdlines] == [([], 'one'), ([1], '# two'), ([1], 'three'), ([2], '# four')]
