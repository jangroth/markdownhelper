import pytest

from markdown_helper import MarkdownLine, MarkdownParser, MarkdownHeading, HeadingIndices, MarkdownDocument


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

    line = mdp.parse(['## foo bar'])[0]
    assert isinstance(line, MarkdownHeading)
    assert line.raw_text == '## foo bar'
    assert line.heading_level == 2


def test_should_convert_both_to_markdown(mdp):
    lines = mdp.parse(['# bar', 'foo'])
    assert lines[0].to_markdown() == ['# bar']
    assert lines[1].to_markdown() == ['foo']


def test_should_convert_mh_to_toc_entry(mdp):
    line = mdp.parse(['# foo'])[0]
    assert line.to_toc_entry() == '* [foo](#1)'
    line = mdp.parse(['# foo', '## bar baz'])[1]
    assert line.to_toc_entry() == '  * [bar baz](#1_1)'


def test_dont_render_navlink_if_target_doesnt_exist(mdp):
    line = mdp.parse(['# foo'])[0]
    assert line.to_markdown(with_anchor=True) == ['<a name="1"></a>', '# [↖](#top) foo']


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
    assert mdd._remove_existing_tocs(['foo', mdd.TOC_START[0], 'bar', mdd.TOC_END[-1], 'baz']) == ['foo', 'baz']
    assert mdd._remove_existing_tocs(['foo', mdd.TOC_START[0], 'bar', mdd.TOC_END[-1], 'baz', 'foo', mdd.TOC_START[0], 'bar', mdd.TOC_END[-1], 'baz']) == ['foo', 'baz', 'foo', 'baz']


def test_should_fail_if_trying_to_remove_unbalanced_toc(mdd):
    with pytest.raises(AssertionError):
        mdd._remove_existing_tocs([mdd.TOC_START[0]])
    with pytest.raises(AssertionError):
        mdd._remove_existing_tocs([mdd.TOC_END[-1]])
    with pytest.raises(AssertionError):
        mdd._remove_existing_tocs([mdd.TOC_END[-1], mdd.TOC_START[0]])


def test_should_cleanse_old_toc(mdp):
    md_lines_with_old_toc = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    cleansed_lines = list(MarkdownDocument._cleansing_generator([str(line) for line in md_lines_with_old_toc]))
    assert cleansed_lines == ['foo', '# bar', '## bum', '### baz', '# klo']


def test_should_determine_if_toc_needs_to_be_inserted(mdd):
    lines = MarkdownParser().parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    assert mdd._should_insert_toc_here(False) is False
    assert mdd._should_insert_toc_here(True) is True
    assert mdd._should_insert_toc_here(True, lines[0], 0, 0) is False

    assert mdd._should_insert_toc_here(True, lines[2], 2, 4) is True
    assert mdd._should_insert_toc_here(True, lines[2], 2, 2) is False
    assert mdd._should_insert_toc_here(True, lines[3], 1, 2) is False


def test_should_determine_if_line_is_in_toc(mdd):
    lines = MarkdownParser().parse(['foo', '# bar', '## bum', '### baz', '# klo'])

    assert mdd._is_in_toc(lines[1], (), 0, 0) is True
    assert mdd._is_in_toc(lines[1], (), 0, 1) is True

    assert mdd._is_in_toc(lines[2], (), 0, 0) is True
    assert mdd._is_in_toc(lines[2], (), 0, 1) is False
    assert mdd._is_in_toc(lines[2], (), 0, 2) is True

    assert mdd._is_in_toc(lines[3], (), 0, 0) is True
    assert mdd._is_in_toc(lines[3], (), 0, 1) is False
    assert mdd._is_in_toc(lines[3], (), 0, 2) is False
    assert mdd._is_in_toc(lines[3], (), 0, 3) is True

    assert mdd._is_in_toc(lines[2], (1,), 2, 3) is True
    assert mdd._is_in_toc(lines[2], (1,), 3, 3) is False
    assert mdd._is_in_toc(lines[2], (2,), 2, 3) is False

    assert mdd._is_in_toc(lines[3], (1, 1), 1, 2) is False


def test_is_in_toc_should_fail_if_called_with_markdownline(mdd):
    line = MarkdownParser().parse(['foo'])[0]

    with pytest.raises(AssertionError):
        mdd._is_in_toc(line, (), 0, 0)


def test_should_only_insert_toc_if_it_has_elements(mdp, mdd):
    lines = mdp.parse(['foo'])
    mdd.md_lines = lines
    assert mdd._insert_toc((), 0, 1) == []


def test_should_dump_no_extras(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump() == ['foo', '# bar', '## bum', '### baz', '# klo']


def test_should_dump_with_debug(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_debug=True) == ['foo', '# (1,) bar', '## (1, 1) bum', '### (1, 1, 1) baz', '# (2,) klo']


def test_should_dump_with_main_toc(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True) == ['[toc_start]::', '<a name="top"></a>', '---', '* [bar](#1)', '  * [bum](#1_1)', '    * [baz](#1_1_1)', '* [klo](#2)', '---', '[toc_end]::', 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '<a name="1_1"></a>', '## [↖](#top)[↑](#1)[↓](#1_1_1) bum', '<a name="1_1_1"></a>', '### [↖](#top)[↑](#1_1)[↓](#2) baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']
    assert mdd.dump(with_toc=True, max_main_toc_level=1) == ['[toc_start]::', '<a name="top"></a>', '---', '* [bar](#1)', '* [klo](#2)', '---', '[toc_end]::', 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '## bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']


def test_should_dump_with_main_and_sub_toc(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True, max_main_toc_level=1, extra_sub_toc_level=1) == ['[toc_start]::', '<a name="top"></a>', '---', '* [bar](#1)', '* [klo](#2)', '---', '[toc_end]::', 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '[toc_start]::', '<a name="top"></a>', '---', '  * [bum](#1_1)', '---', '[toc_end]::', '<a name="1_1"></a>', '## [↖](#top)[↑](#1)[↓](#1_1_1) bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']
    assert mdd.dump(with_toc=True, max_main_toc_level=1, extra_sub_toc_level=2) == ['[toc_start]::', '<a name="top"></a>', '---', '* [bar](#1)', '* [klo](#2)', '---', '[toc_end]::', 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '[toc_start]::', '<a name="top"></a>', '---', '  * [bum](#1_1)', '    * [baz](#1_1_1)', '---', '[toc_end]::', '<a name="1_1"></a>', '## [↖](#top)[↑](#1)[↓](#1_1_1) bum', '<a name="1_1_1"></a>', '### [↖](#top)[↑](#1_1)[↓](#2) baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']


def test_should_not_render_anchors_if_line_is_not_linked_to(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True, max_main_toc_level=1) == ['[toc_start]::', '<a name="top"></a>', '---', '* [bar](#1)', '* [klo](#2)', '---', '[toc_end]::', 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '## bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']


def test_should_render_navigation_links(mdp, mdd):
    lines = mdp.parse(['foo', '# bar', '## bum', '### baz', '# klo'])
    mdd.md_lines = lines
    assert mdd.dump(with_toc=True, max_main_toc_level=1) == ['[toc_start]::', '<a name="top"></a>', '---', '* [bar](#1)', '* [klo](#2)', '---', '[toc_end]::', 'foo', '<a name="1"></a>', '# [↖](#top)[↓](#1_1) bar', '## bum', '### baz', '<a name="2"></a>', '# [↖](#top)[↑](#1_1_1) klo']
