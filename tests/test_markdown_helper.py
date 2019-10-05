import pytest

from markdown_helper import MarkdownLine, MarkdownHelper, MarkdownDocument


@pytest.fixture
def mdl():
    return MarkdownLine.__new__(MarkdownLine)


@pytest.fixture
def mdd():
    return MarkdownDocument.__new__(MarkdownDocument)


@pytest.fixture
def mdh():
    return MarkdownHelper.__new__(MarkdownHelper)


REMOVE_OLD_TOC = True
WITH_ANCHOR = True
WITHOUT_ANCHOR = False
WITH_DEBUG = True


def test_should_equal_and_not_equal():
    md1 = MarkdownLine('a')
    md2 = MarkdownLine('a')
    md3 = MarkdownLine('# b', (1,))
    assert md1 == md2
    assert md1 != md3
    assert str(md3) == '(2,):# b'


def test_should_create_anchor_name_from_index(mdl):
    mdl._current_index = [1, 2]
    assert mdl.anchor_name == '1_2'
    mdl._current_index = []
    assert mdl.anchor_name == ''


def test_should_get_header_level_from_line(mdl):
    assert mdl._get_header_level('') == 0
    assert mdl._get_header_level('# adsf') == 1
    assert mdl._get_header_level('## adsf') == 2
    assert mdl._get_header_level('# #') == 1
    assert mdl._get_header_level(' ##') == 0


def test_calculate_new_index(mdl):
    assert mdl._generate_index((), 'test') == ()
    assert mdl._generate_index((1,), 'test') == ()

    assert mdl._generate_index((), '# test') == (1,)
    assert mdl._generate_index((2,), '## test') == (2, 1)

    assert mdl._generate_index((1,), '# test') == (2,)
    assert mdl._generate_index((1, 2), '## test') == (1, 3)

    assert mdl._generate_index((1, 2), '# test') == (2,)
    assert mdl._generate_index((1, 2, 3), '## test') == (1, 3)


def test_should_render_link_to_top():
    assert MarkdownLine('a').link_to_top == '[↖](#top)'


def test_should_render_link_to_previous():
    assert MarkdownLine('### a', (1, 2)).link_to_previous == '[↑](#1_2)'
    assert MarkdownLine('## a', (1, 2)).link_to_previous == '[↑](#1_2)'


def test_should_render_to_markdown():
    assert MarkdownLine('a').to_markdown() == 'a'
    assert MarkdownLine('a').to_markdown(WITH_ANCHOR, WITH_DEBUG) == 'a'
    assert MarkdownLine('# 1').to_markdown() == '# [↖](#top)[↑](#)[↓](#) 1'
    assert MarkdownLine('# 1').to_markdown(WITHOUT_ANCHOR, WITH_DEBUG) == '# [↖](#top)[↑](#)[↓](#)(1,) -  1'
    assert MarkdownLine('# 1').to_markdown(WITH_ANCHOR, WITH_DEBUG) == '<a name="1"></a>\n# [↖](#top)[↑](#)[↓](#)(1,) -  1'
    assert MarkdownLine('# 1').to_markdown(WITH_ANCHOR) == '<a name="1"></a>\n# [↖](#top)[↑](#)[↓](#) 1'


def test_should_render_to_toc_entry():
    assert MarkdownLine('a').to_toc_entry() == 'a'
    assert MarkdownLine('# a').to_toc_entry() == '* [a](#1)'
    assert MarkdownLine('## a', [1]).to_toc_entry() == '  * [a](#1_1)'


def test_dont_cleanse_text_line(mdd):
    assert list(mdd._cleansing_generator(['abc'])) == ['abc']


def test_cleanse_markdown_line_back_to_original(mdd):
    md_lines = MarkdownLine('# abc').to_markdown(WITH_ANCHOR).split('\n')
    assert list(mdd._cleansing_generator(md_lines)) == ['# abc']
    md_lines = MarkdownLine('## abc', (1, 1), (1, 3)).to_markdown(WITH_ANCHOR).split('\n')
    assert list(mdd._cleansing_generator(md_lines)) == ['## abc']


def test_cleanse_old_toc(mdd):
    lines = ['before', '', '[toc_start]::', 'foobar', '', '[toc_end]::', 'after']
    assert mdd._remove_old_toc(lines) == ['before', 'after']


def test_cleanse_multiple_lines(mdd):
    lines = ['[top](#top)', '# two<a name="foo"></a>']
    assert list(mdd._cleansing_generator(lines)) == ['# two']


def test_convert_multiple_lines(mdd):
    md_data = [(md_line.index, md_line.line) for md_line in mdd._cleansed_to_md(['one', '# two', 'three', '# four'])]
    assert md_data == [((), 'one'), ((1,), '# two'), ((), 'three'), ((2,), '# four')]


def test_add_next_indices_to_md(mdd):
    md_lines = mdd._cleansed_to_md(['one', '# two', 'three', '# four'])
    md_lines_with_next_indices = mdd._add_next_indices_to_md(md_lines)
    assert md_lines_with_next_indices[1]._next_index == (2,)
