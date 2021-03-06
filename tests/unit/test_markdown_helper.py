import re

import pytest

from markdown_helper import MarkdownParser, MarkdownDocument, MarkdownLine, MarkdownHeading, HeadingIndices


@pytest.fixture
def mdp():
    return MarkdownParser()


@pytest.fixture
def mdd():
    return MarkdownDocument.__new__(MarkdownDocument)


# --- markdownline/heading tests

def test_should_recognize_non_heading(mdp):
    line = mdp.parse(['foo'])[0]
    assert isinstance(line, MarkdownLine)
    assert line.raw_text == 'foo'

    line = mdp.parse(['#foo bar'])[0]
    assert isinstance(line, MarkdownLine)
    assert line.raw_text == '#foo bar'


def test_should_recognize_heading(mdp):
    line = mdp.parse(['# foo'])[0]
    assert isinstance(line, MarkdownHeading)
    assert line.raw_text == '# foo'
    assert line.heading_level == 1

    line = mdp.parse(['## foo (bar)'])[0]
    assert isinstance(line, MarkdownHeading)
    assert line.raw_text == '## foo (bar)'
    assert line.heading_level == 2


def test_should_convert_both_to_markdown(mdp):
    lines = mdp.parse(['# bar', 'foo'])
    assert lines[0].to_markdown() == ['# bar']
    assert lines[1].to_markdown() == ['foo']


def test_should_convert_mh_to_toc_entry(mdp):
    line = mdp.parse(['# foo'])[0]
    assert line.to_toc_entry(0) == '* [foo](#1)'
    line = mdp.parse(['# foo', '## bar baz'])[1]
    assert line.to_toc_entry(0) == '  * [bar baz](#1_1)'
    line = mdp.parse(['# foo', '## bar (baz)'])[1]
    assert line.to_toc_entry(0) == '  * [bar (baz)](#1_1)'


def test_dont_render_navlink_if_target_doesnt_exist(mdp):
    line = mdp.parse(['# foo'])[0]
    assert line.to_markdown(with_anchor=True) == ['<a name="1"></a>', '# [↖](#top) foo']


def test_link_to_top_should_point_to_sub_toc_if_appropriate(mdp):
    lines = mdp.parse(['# foo', '## foo', '### foo', '### bar'])
    line = lines[0]
    assert line.to_markdown(with_anchor=True, top_level=1) == ['<a name="1"></a>', '# [↖](#top)[↓](#1_1) foo']
    assert line.to_markdown(with_anchor=True, top_level=2) == ['<a name="1"></a>', '# [↖](#top)[↓](#1_1) foo']
    line = lines[1]
    assert line.to_markdown(with_anchor=True, top_level=1) == ['<a name="1_1"></a>', '## [↖](#1)[↑](#1)[↓](#1_1_1) foo']
    assert line.to_markdown(with_anchor=True, top_level=2) == ['<a name="1_1"></a>', '## [↖](#top)[↑](#1)[↓](#1_1_1) foo']
    line = lines[2]
    assert line.to_markdown(with_anchor=True, top_level=1) == ['<a name="1_1_1"></a>', '### [↖](#1)[↑](#1_1)[↓](#1_1_2) foo']
    assert line.to_markdown(with_anchor=True, top_level=2) == ['<a name="1_1_1"></a>', '### [↖](#1_1)[↑](#1_1)[↓](#1_1_2) foo']
    line = lines[3]
    assert line.to_markdown(with_anchor=True, top_level=1) == ['<a name="1_1_2"></a>', '### [↖](#1)[↑](#1_1_1) bar']
    assert line.to_markdown(with_anchor=True, top_level=2) == ['<a name="1_1_2"></a>', '### [↖](#1_1)[↑](#1_1_1) bar']


# --- parser tests

def test_calculate_new_index(mdp):
    assert mdp._generate_index((), 1) == (1,)
    assert mdp._generate_index((2,), 2) == (2, 1)

    assert mdp._generate_index((1,), 1) == (2,)
    assert mdp._generate_index((1, 2), 2) == (1, 3)

    assert mdp._generate_index((1, 2), 1) == (2,)
    assert mdp._generate_index((1, 2, 3), 2) == (1, 3)

    assert mdp._generate_index((2, 1, 6, 7), 2) == (2, 2)


def test_should_fail_if_generate_index_is_called_for_zero_heading_level():
    with pytest.raises(AttributeError):
        mdp._generate_index((), 0)


def test_should_parse(mdp):
    lines = mdp.parse(['foo', '# bar', 'bas', '# bum'])
    assert lines[1].heading_indices == HeadingIndices(previous=(), current=(1,), next=(2,))
    assert lines[3].heading_indices == HeadingIndices(previous=(1,), current=(2,), next=())


# --- mdd tests


def test_should_remove_existing_tocs(mdd):
    assert mdd._remove_existing_tocs([]) == []
    assert mdd._remove_existing_tocs(['foo']) == ['foo']
    assert mdd._remove_existing_tocs(['foo', mdd.TOC_EMPTY_LINE, mdd.TOC_START, 'bar', mdd.TOC_EMPTY_LINE, mdd.TOC_END, 'baz']) == ['foo', 'baz']
    assert mdd._remove_existing_tocs(['foo', mdd.TOC_EMPTY_LINE, mdd.TOC_START, 'bar', mdd.TOC_EMPTY_LINE, mdd.TOC_END, 'baz', 'foo', mdd.TOC_EMPTY_LINE, mdd.TOC_START, 'bar', mdd.TOC_EMPTY_LINE, mdd.TOC_END, 'baz']) == ['foo', 'baz', 'foo', 'baz']


def test_should_fail_if_trying_to_remove_unbalanced_toc(mdd):
    with pytest.raises(AssertionError):
        mdd._remove_existing_tocs([mdd.TOC_START])
    with pytest.raises(AssertionError):
        mdd._remove_existing_tocs([mdd.TOC_END])
    with pytest.raises(AssertionError):
        mdd._remove_existing_tocs([mdd.TOC_END, mdd.TOC_START])


def test_reg_ex_for_internal_link(mdd):
    test_ex = MarkdownDocument.REG_INTERNAL_LINK
    assert re.sub(test_ex, '', "##[↖](#top)[↑](#1_1)[↓](#2) Laudem persius") == '## Laudem persius'
    assert re.sub(test_ex, '', "##[↖](#top)[↑](#1_1)[↓](#2) Laudem persius (core)") == '## Laudem persius (core)'
    assert re.sub(test_ex, '', "##[↖](#top)[↑](#1_1)[↓](#2) Laudem (core) persius") == '## Laudem (core) persius'


def test_should_cleanse_old_tocs_and_anchors_and_nav_links(mdd):
    mdd.md_lines = MarkdownParser().parse(['foo', '# bar (core)', '## bum', '### baz', '# klo'])
    result = mdd.dump(with_toc=True, with_navigation_arrows=True)
    cleansed_lines = list(MarkdownDocument._cleansing_generator([str(line) for line in result]))
    assert cleansed_lines == ['foo', '# bar (core)', '## bum', '### baz', '# klo']


def test_should_determine_if_toc_needs_to_be_inserted(mdd):
    lines = MarkdownParser().parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    assert mdd._should_insert_toc_here(False) is False
    assert mdd._should_insert_toc_here(True) is True
    assert mdd._should_insert_toc_here(True, lines[0], 0, 0) is False

    assert mdd._should_insert_toc_here(True, lines[2], 2, 4) is True
    assert mdd._should_insert_toc_here(True, lines[2], 2, 2) is False
    assert mdd._should_insert_toc_here(True, lines[3], 1, 2) is False


def test_should_determine_if_line_is_in_toc(mdd):
    lines = MarkdownParser().parse(['foo', '# bar', '## bum (core)', '### baz', '# klo'])

    assert mdd._is_line_in_toc(lines[1], (), 0, 0) is True
    assert mdd._is_line_in_toc(lines[1], (), 0, 1) is True

    assert mdd._is_line_in_toc(lines[2], (), 0, 0) is True
    assert mdd._is_line_in_toc(lines[2], (), 0, 1) is False
    assert mdd._is_line_in_toc(lines[2], (), 0, 2) is True

    assert mdd._is_line_in_toc(lines[3], (), 0, 0) is True
    assert mdd._is_line_in_toc(lines[3], (), 0, 1) is False
    assert mdd._is_line_in_toc(lines[3], (), 0, 2) is False
    assert mdd._is_line_in_toc(lines[3], (), 0, 3) is True

    assert mdd._is_line_in_toc(lines[2], (1,), 2, 3) is True
    assert mdd._is_line_in_toc(lines[2], (1,), 3, 3) is False
    assert mdd._is_line_in_toc(lines[2], (2,), 2, 3) is False

    assert mdd._is_line_in_toc(lines[3], (1, 1), 1, 2) is False


def test_is_in_toc_should_fail_if_called_with_markdownline(mdd):
    line = MarkdownParser().parse(['foo'])[0]

    with pytest.raises(AssertionError):
        mdd._is_line_in_toc(line, (), 0, 0)


def test_should_only_return_toc_if_it_has_elements(mdp, mdd):
    lines = mdp.parse(['foo'])
    mdd.md_lines = lines
    assert mdd._create_toc((), 0, 1) == []


def test_should_dump_no_extras(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum (core)', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump() == ['foo', '# bar', '## bum (core)', '### baz', '# klo']


def test_should_dump_with_debug(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_debug=True) == ['foo', '# (1,) bar', '## (1, 1) bum', '### (1, 1, 1) baz', '# (2,) klo']


def test_should_dump_with_main_toc(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True) == [MarkdownDocument.TOC_START, MarkdownDocument.TOC_TOP_ANCHOR, MarkdownDocument.TOC_RULER, '* [bar](#1)', '  * [bum](#1_1)', '    * [baz](#1_1_1)', '* [klo](#2)', MarkdownDocument.TOC_RULER, MarkdownDocument.TOC_END, 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '<a name="1_1"></a>', '## [↖](#top)[↑](#1)[↓](#1_1_1) bum', '<a name="1_1_1"></a>', '### [↖](#top)[↑](#1_1)[↓](#2) baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']
    assert mdd.dump(with_toc=True, max_main_toc_level=1) == [MarkdownDocument.TOC_START, MarkdownDocument.TOC_TOP_ANCHOR, MarkdownDocument.TOC_RULER, '* [bar](#1)', '* [klo](#2)', MarkdownDocument.TOC_RULER, MarkdownDocument.TOC_END, 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '## bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']


def test_should_dump_with_main_and_sub_toc(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True, max_main_toc_level=1, extra_sub_toc_level=1) == [MarkdownDocument.TOC_START, MarkdownDocument.TOC_TOP_ANCHOR, MarkdownDocument.TOC_RULER, '* [bar](#1)', '* [klo](#2)', MarkdownDocument.TOC_RULER, MarkdownDocument.TOC_END, 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', MarkdownDocument.TOC_START, '* [bum](#1_1)', MarkdownDocument.TOC_END, '<a name="1_1"></a>', '## [↖](#1)[↑](#1)[↓](#1_1_1) bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']
    assert mdd.dump(with_toc=True, max_main_toc_level=1, extra_sub_toc_level=2) == [MarkdownDocument.TOC_START, MarkdownDocument.TOC_TOP_ANCHOR, MarkdownDocument.TOC_RULER, '* [bar](#1)', '* [klo](#2)', MarkdownDocument.TOC_RULER, MarkdownDocument.TOC_END, 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', MarkdownDocument.TOC_START, '* [bum](#1_1)', '  * [baz](#1_1_1)', MarkdownDocument.TOC_END, '<a name="1_1"></a>', '## [↖](#1)[↑](#1)[↓](#1_1_1) bum', '<a name="1_1_1"></a>', '### [↖](#1)[↑](#1_1)[↓](#2) baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']


def test_should_not_render_anchors_if_line_is_not_linked_to(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True, max_main_toc_level=1) == [MarkdownDocument.TOC_START, MarkdownDocument.TOC_TOP_ANCHOR, MarkdownDocument.TOC_RULER, '* [bar](#1)', '* [klo](#2)', MarkdownDocument.TOC_RULER, MarkdownDocument.TOC_END, 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '## bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']


def test_should_render_navigation_links(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True, max_main_toc_level=1) == [MarkdownDocument.TOC_START, MarkdownDocument.TOC_TOP_ANCHOR, MarkdownDocument.TOC_RULER, '* [bar](#1)', '* [klo](#2)', MarkdownDocument.TOC_RULER, MarkdownDocument.TOC_END, 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '## bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']
