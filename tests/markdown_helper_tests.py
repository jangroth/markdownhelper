import pytest

from markdown_helper import MarkdownLine, MarkdownHelper


@pytest.fixture
def mdl():
    return MarkdownLine.__new__(MarkdownLine)


@pytest.fixture
def mdh():
    return MarkdownHelper.__new__(MarkdownHelper)


def test_should_equal_and_not_equal():
    md1 = MarkdownLine('a')
    md2 = MarkdownLine('a')
    md3 = MarkdownLine('# b', [1])
    assert md1 == md2
    assert md1 != md3
    assert str(md3) == '[2] - # b'


def test_should_create_anchor_name_from_index(mdl):
    mdl._index = [1, 2]
    assert mdl.anchor_name == '1_2'
    mdl._index = []
    assert mdl.anchor_name == ''


def test_should_get_header_level_from_line(mdl):
    assert mdl._get_header_level('') == 0
    assert mdl._get_header_level('# adsf') == 1
    assert mdl._get_header_level('## adsf') == 2
    assert mdl._get_header_level('# #') == 1
    assert mdl._get_header_level(' ##') == 0


def test_calculate_new_index(mdl):
    assert mdl._generate_index([], 'test') == []
    assert mdl._generate_index([1], 'test') == []

    assert mdl._generate_index([], '# test') == [1]
    assert mdl._generate_index([2], '## test') == [2, 1]

    assert mdl._generate_index([1], '# test') == [2]
    assert mdl._generate_index([1, 2], '## test') == [1, 3]

    assert mdl._generate_index([1, 2], '# test') == [2]
    assert mdl._generate_index([1, 2, 3], '## test') == [1, 3]


def test_cleanse_line(mdh):
    assert list(mdh._cleansing_generator(['\n'])) == ['']
    assert list(mdh._cleansing_generator(['abc'])) == ['abc']
    assert list(mdh._cleansing_generator(['abc\n'])) == ['abc']
    assert list(mdh._cleansing_generator(['## EC2 Autoscaling Concepts<a name="asc"></a>'])) == ['## EC2 Autoscaling Concepts']
    assert list(mdh._cleansing_generator(['[top](#top)test'])) == ['test']
    assert list(mdh._cleansing_generator(['[top](#top)'])) == []


def test_cleanse_multiple_lines(mdh):
    assert mdh._raw_to_cleansed(['[top](#top)', '# two<a name="foo"></a>']) == ['# two']


def test_convert_multiple_lines(mdh):
    md_data = [(md_line.index, md_line.line) for md_line in mdh._cleansed_to_md(['one', '# two', 'three', '# four'])]
    assert md_data == [([], 'one'), ([1], '# two'), ([], 'three'), ([2], '# four')]
