import re
from collections import namedtuple
from typing import List, Tuple

HeadingIndices = namedtuple('HeadingIndices', ['previous', 'current', 'next'])


class MarkdownLine:

    def __init__(self, text: str):
        self.raw_text = text

    def __str__(self):
        return self.raw_text

    def to_markdown(self, with_anchor=False, top_level=0, sub_level=0, with_debug=False) -> List[str]:
        return [self.raw_text]

    def to_toc_entry(self) -> str:
        raise NotImplementedError()


class MarkdownHeading(MarkdownLine):
    def __init__(self, text: str):
        super().__init__(text)
        self.heading, _, self.text_after_heading = text.partition(" ")
        self.heading_level = len(self.heading)
        self.heading_indices = None

    @staticmethod
    def _anchor_name(tpl: Tuple[int]) -> str:
        return '_'.join([str(i) for i in tpl])

    def _complete_anchor(self) -> str:
        return f'<a name="{MarkdownHeading._anchor_name(self.heading_indices.current)}"></a>'

    def to_toc_entry(self) -> str:
        return f'{"  " * (self.heading_level - 1)}' \
               f'* ' \
               f'[{self.text_after_heading}](#{MarkdownHeading._anchor_name(self.heading_indices.current)})'

    def link_to_top(self):
        return '[↖](#top)'

    def link_to_previous(self):
        # TODO: only render if exists
        return f'[↑](#{MarkdownHeading._anchor_name(self.heading_indices.previous)})'

    def link_to_next(self):
        # TODO: only render if exists
        return f'[↓](#{MarkdownHeading._anchor_name(self.heading_indices.next)})'

    def to_markdown(self, with_anchor=False, top_level=0, sub_level=0, with_debug=False) -> List[str]:
        result = []
        if with_anchor:
            result.append(self._complete_anchor())
        navigation_links_part = f'{self.link_to_top()}{self.link_to_previous()}{self.link_to_next()} ' if with_anchor else ''
        debug_part = f'{self.heading_indices.current} ' if with_debug else ''
        result.append(f'{self.heading} {navigation_links_part}{debug_part}{self.text_after_heading}')
        return result


class MarkdownParser:
    REG_HEADING_CHAR = re.compile('^#+ .+')

    def _is_heading(self, line: str) -> bool:
        return re.match(self.REG_HEADING_CHAR, line) is not None

    @staticmethod
    def _add_new_level(index: Tuple[int]) -> Tuple[int]:
        return (*index, 1)

    @staticmethod
    def _bump_last_level(index: Tuple[int]) -> Tuple[int]:
        return index[:-1] + (index[-1] + 1,)

    @staticmethod
    def _remove_obsolete_levels(index: Tuple[int], current_level: int) -> Tuple[int]:
        return index[:current_level]

    def _generate_index(self, previous_index: Tuple[int], current_header_level: int) -> Tuple[int]:
        assert current_header_level > 0
        previous_level = len(previous_index)
        if current_header_level > previous_level:
            return self._add_new_level(previous_index)
        elif current_header_level == previous_level:
            return self._bump_last_level(previous_index)
        else:
            shortened_index = self._remove_obsolete_levels(previous_index, current_header_level)
            return self._bump_last_level(shortened_index)

    def _set_next_index(self, lines: List[str]):
        current_index = ()
        for heading in (heading for heading in reversed(lines) if isinstance(heading, MarkdownHeading)):
            next_index = heading.heading_indices.current
            heading.heading_indices = HeadingIndices(heading.heading_indices.previous, heading.heading_indices.current, current_index)
            current_index = next_index

    def _set_prev_and_current_index(self, lines: List[str]):
        current_index = ()
        for heading in (heading for heading in lines if isinstance(heading, MarkdownHeading)):
            new_index = self._generate_index(current_index, heading.heading_level)
            heading.heading_indices = HeadingIndices(current_index, new_index, None)
            current_index = new_index

    def parse(self, lines: List[str]) -> List[MarkdownLine]:
        lines = [MarkdownHeading(line) if self._is_heading(line) else MarkdownLine(line) for line in lines]
        self._set_prev_and_current_index(lines)
        self._set_next_index(lines)
        return lines


class MarkdownDocument:
    REG_SPACER_BETWEEN_HEADER_AND_LINK = re.compile('(?<=#) (?=\\[)')
    REG_INTERNAL_ANCHOR = re.compile('<a.*name.*a>')
    REG_INTERNAL_LINK = re.compile('\\[.*\\]\\(#.*\\)')
    TOC_START = ['[toc_start]::', '<a name="top"></a>', '---']
    TOC_END = ['---', '[toc_end]::']

    def __init__(self, raw_lines, remove_old_toc=False):
        if remove_old_toc:
            raw_lines = list(self._cleansing_generator(raw_lines))
        self.md_lines = MarkdownParser().parse(raw_lines)

    @staticmethod
    def _cleansing_generator(lines: List[str]) -> str:
        lines = MarkdownDocument._remove_existing_tocs(lines)
        for line in lines:
            if line != '':
                line = re.sub(MarkdownDocument.REG_SPACER_BETWEEN_HEADER_AND_LINK, '', line)
                line = re.sub(MarkdownDocument.REG_INTERNAL_ANCHOR, '', line)
                line = re.sub(MarkdownDocument.REG_INTERNAL_LINK, '', line)
                if line:
                    yield line
            else:
                yield line

    @staticmethod
    def _remove_existing_tocs(lines: List[str]) -> List[str]:
        try:
            while True:
                start = lines.index(MarkdownDocument.TOC_START[0])
                end = lines.index(MarkdownDocument.TOC_END[-1])
                assert start < end
                lines = [line for index, line in enumerate(lines) if index < start or index > end]
        except ValueError:
            pass
        assert all(x not in [MarkdownDocument.TOC_START[0], MarkdownDocument.TOC_END[-1]] for x in lines)
        return lines

    def _insert_toc(self, toc_parent_index, start_level, end_level):
        result = []
        toc_lines = [line.to_toc_entry() for line in self.md_lines if isinstance(line, MarkdownHeading) and self._is_in_toc(line, toc_parent_index, start_level, end_level)]
        if toc_lines:
            result.extend(self.TOC_START)
            result.extend(toc_lines)
            result.extend(self.TOC_END)
        return result

    def _is_in_toc(self, line, toc_parent_index, start_level, end_level):
        assert isinstance(line, MarkdownHeading)

        parent_len = len(toc_parent_index)
        current = line.heading_indices.current
        if current[:parent_len] == toc_parent_index:
            end_level_if_provided_or_always_greater = end_level if end_level != 0 else line.heading_level + 1
            if start_level <= line.heading_level <= end_level_if_provided_or_always_greater:
                return True
        return False

    def _should_insert_toc_here(self, with_toc, line=None, max_main_toc_level=None, max_sub_toc_level=None):
        if not with_toc:
            return False
        else:
            if not (line or max_main_toc_level or max_sub_toc_level):
                return True
            else:
                if not isinstance(line, MarkdownHeading):
                    return False
                is_correct_start_level_for_sub_toc = line.heading_level == max_main_toc_level
                has_sub_levels_to_render = line.heading_level < max_sub_toc_level
                return is_correct_start_level_for_sub_toc and has_sub_levels_to_render

    def _needs_anchor(self, md_line, with_toc, max_main_toc_level, extra_sub_toc_level):
        if not with_toc or not isinstance(md_line, MarkdownHeading):
            return False
        if max_main_toc_level == 0:
            return True
        else:
            return md_line.heading_level <= max_main_toc_level + extra_sub_toc_level

    def dump(self, with_toc=False, with_navigation_arrows=False, with_debug=False, max_main_toc_level=0, extra_sub_toc_level=0):
        lines = []
        if self._should_insert_toc_here(with_toc):
            lines.extend(self._insert_toc((), 0, max_main_toc_level))
        for md_line in self.md_lines:
            with_anchor = self._needs_anchor(md_line, with_toc, max_main_toc_level, extra_sub_toc_level)
            lines.extend(md_line.to_markdown(with_anchor=with_anchor, top_level=max_main_toc_level, sub_level=extra_sub_toc_level, with_debug=with_debug))
            if self._should_insert_toc_here(with_toc, md_line, max_main_toc_level, max_main_toc_level + extra_sub_toc_level):
                lines.extend(self._insert_toc(md_line.heading_indices.current, md_line.heading_level + 1, md_line.heading_level + extra_sub_toc_level))
        return lines


class MarkdownHelper:

    def __init__(self, path):
        self.raw_content = self._read_from_file(path)

    @staticmethod
    def _read_from_file(path):
        with open(path) as file:
            return [line.rstrip('\n') for line in file]

    @staticmethod
    def _print_content(content):
        print('\n'.join(content))

    def dump(self, add_toc=False, remove_old_toc=False, with_debug=False):
        md_document = MarkdownDocument(raw_lines=self.raw_content, remove_old_toc=remove_old_toc)
        content = md_document.dump(with_toc=add_toc, with_debug=with_debug)
        self._print_content(content)

    def cleanse(self):
        md_document = MarkdownDocument(raw_lines=self.raw_content, remove_old_toc=True)
        content = md_document.dump()
        self._print_content(content)

    def add_toc(self, add_navigation=False, top_level=0, sub_level=0):
        md_document = MarkdownDocument(raw_lines=self.raw_content, remove_old_toc=True)
        content = md_document.dump(with_toc=True, with_navigation_arrows=add_navigation, max_main_toc_level=top_level, extra_sub_toc_level=sub_level)
        self._print_content(content)


class MarkdownLineThingy:
    REG_HEADER_CHAR = re.compile('^#*')

    def __init__(self, line, previous_index=(), next_index=()):
        self._line = line
        self._previous_index = previous_index
        self._current_index = self._generate_index_for_line(previous_index, line)
        self._next_index = next_index

    def _generate_index_for_line(self, previous_index, line):
        previous_level = len(previous_index)
        current_level = self._get_header_level(line)
        if current_level:
            if current_level > previous_level:
                return self._add_new_level(previous_index)
            elif current_level == previous_level:
                return self._bump_last_level(previous_index)
            elif current_level < previous_level:
                shortened_index = self._remove_obsolete_levels(previous_index, current_level)
                return self._bump_last_level(shortened_index)
        else:
            return ()

    @staticmethod
    def _get_header_level(line):
        check = re.search(MarkdownLineThingy.REG_HEADER_CHAR, line)
        return check.span()[1] if check else 0

    @staticmethod
    def _add_new_level(index):
        return (*index, 1)

    @staticmethod
    def _bump_last_level(index):
        return index[:-1] + (index[-1] + 1,)

    @staticmethod
    def _remove_obsolete_levels(index, current_level):
        return index[:current_level]

    def __str__(self):
        return f'{self._current_index}:{self._line}'

    def __repr__(self):
        return f'MarkdownLine(line={self.line}, previous_index={self._previous_index}, next_index={self._next_index})'

    def __eq__(self, other):
        if not isinstance(other, MarkdownLineThingy):
            return NotImplemented
        return self._line == other._line and self._current_index == other._current_index

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self._line, self._current_index))

    @staticmethod
    def _to_anchor_name(index):
        return '_'.join([str(i) for i in index])

    def _get_text_part(self):
        return self.line.partition(" ")[2]

    def _get_debug_part(self, with_debug):
        return f'{self.index} ' if self.index and with_debug else ''

    def _get_index_part(self):
        level = '#' * self.header_level
        return f'{level} '

    def _get_navigation_part(self, top_level, with_navigation):
        return f'{self.link_to_top}{self.link_to_previous}{self.link_to_next} ' if with_navigation and (top_level == 0 or self.header_level <= top_level) else ''

    def set_next_index(self, next_index):
        self._next_index = next_index

    def to_toc_entry(self):
        return f'{"  " * (self.header_level - 1)}* [{self.line.partition(" ")[2]}](#{self._to_anchor_name(self._current_index)})' if self.index else self.line

    def to_markdown(self, with_anchor=False, with_navigation=False, top_level=0, sub_level=0, with_debug=False):
        if not self.is_header:
            return [self.line]
        else:
            index_part = self._get_index_part()
            navigation_part = self._get_navigation_part(top_level, with_navigation)
            debug_part = self._get_debug_part(with_debug)
            text_part = self._get_text_part()
            complete_line = f'{index_part}{navigation_part}{debug_part}{text_part}'
            if with_anchor and (top_level == 0 or self.header_level <= top_level):
                pre_line = f'<a name="{self.anchor_name}"></a>'
                return [pre_line, complete_line]
            else:
                return [complete_line]

    @property
    def line(self):
        return self._line

    @property
    def index(self):
        return self._current_index

    @property
    def is_header(self):
        return self.index is not ()

    @property
    def header_level(self):
        return len(self.index)

    @property
    def anchor_name(self):
        return '_'.join([str(i) for i in self._current_index])

    @property
    def link_to_top(self):
        return '[↖](#top)'

    @property
    def link_to_previous(self):
        return f'[↑](#{self._to_anchor_name(self._previous_index)})'

    @property
    def link_to_next(self):
        return f'[↓](#{self._to_anchor_name(self._next_index)})'


class MarkdownDocumentThingy:
    REG_SPACER_BETWEEN_HEADER_AND_LINK = re.compile('(?<=#) (?=\\[)')
    REG_INTERNAL_ANCHOR = re.compile('<a.*name.*a>')
    REG_INTERNAL_LINK = re.compile('\\[.*\\]\\(#.*\\)')
    TOC_START = ['[toc_start]::', '<a name="top"></a>', '---']
    TOC_END = ['---', '[toc_end]::']

    def __init__(self, lines, remove_old_toc=False):
        if remove_old_toc:
            lines = list(self._cleansing_generator(lines))
        md_lines_with_previous_index = self._cleansed_to_md(lines)
        self.md_lines = self._add_next_indices_to_md(md_lines_with_previous_index)

    def _cleansing_generator(self, lines):
        lines = self._remove_old_toc(lines)
        for line in lines:
            if line != '':
                line = re.sub(self.REG_SPACER_BETWEEN_HEADER_AND_LINK, '', line)
                line = re.sub(self.REG_INTERNAL_ANCHOR, '', line)
                line = re.sub(self.REG_INTERNAL_LINK, '', line)
                if line:
                    yield line
            else:
                yield line

    @staticmethod
    def _remove_old_toc(lines):
        try:
            start = lines.index(MarkdownDocumentThingy.TOC_START[0])
            end = lines.index(MarkdownDocumentThingy.TOC_END[-1])
            lines = [line for index, line in enumerate(lines) if index < start or index > end]
        except ValueError:
            pass
        return lines

    @staticmethod
    def _cleansed_to_md(lines):
        result = []
        current_index = ()
        for line in lines:
            md_line = MarkdownLineThingy(line=line, previous_index=current_index)
            if md_line.is_header:
                current_index = md_line.index
            result.append(md_line)
        return result

    @staticmethod
    def _add_next_indices_to_md(md_lines):
        result = []
        current_index = ()
        for line in reversed(md_lines):
            if line.is_header:
                line._set_next_index(current_index)
                current_index = line.index
            result.append(line)
        return result[::-1]

    @staticmethod
    def _should_add_to_toc(line_index, toc_parent_index, toc_start_level, toc_end_level):
        result = False
        this_level = len(line_index)
        if line_index:
            if toc_end_level == 0:
                result = True
            elif toc_end_level <= this_level:
                result = True

        return result

    def _insert_toc(self, toc_parent_index, start_level, end_level):
        result = []
        result.extend(self.TOC_START)
        for line in self.md_lines:
            if self._should_add_to_toc(line, toc_parent_index, start_level, end_level):
                result.append(line.to_toc_entry())
        result.extend(self.TOC_END)
        return result

    def dump(self, add_toc=False, add_navigation=False, top_level=0, sub_level=0, with_debug=False):
        lines = []
        if add_toc:
            lines.extend(self._insert_toc((), 0, top_level))
        for md_line in self.md_lines:
            lines.extend(md_line.to_markdown(with_anchor=add_toc, with_navigation=add_navigation, top_level=top_level, sub_level=sub_level, with_debug=with_debug))
            if md_line.is_header and top_level < md_line.header_level <= (top_level + sub_level):
                lines.extend(self._insert_toc(md_line.index, md_line.header_level + 1, md_line.header_level + sub_level))
        return lines
