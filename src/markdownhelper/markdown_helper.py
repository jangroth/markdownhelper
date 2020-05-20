import re
from collections import namedtuple

HeadingIndices = namedtuple('HeadingIndices', ['previous', 'current', 'next'])


class MarkdownLine:

    def __init__(self, text):
        self.raw_text = text

    def __str__(self):
        return self.raw_text

    def to_markdown(self, with_anchor=False, top_level=0, sub_level=0, with_debug=False):
        return [self.raw_text]

    def to_toc_entry(self, base_heading):
        raise NotImplementedError()


class MarkdownHeading(MarkdownLine):
    def __init__(self, text):
        super().__init__(text)
        self.heading, _, self.text_after_heading = text.partition(" ")
        self.heading_level = len(self.heading)
        self.heading_indices = None

    @staticmethod
    def _anchor_name(tpl):
        return '_'.join([str(i) for i in tpl])

    def _complete_anchor(self):
        return f'<a name="{MarkdownHeading._anchor_name(self.heading_indices.current)}"></a>'

    def to_toc_entry(self, base_heading):
        return f'{"  " * (self.heading_level - base_heading - 1)}' \
               f'* ' \
               f'[{self.text_after_heading}](#{MarkdownHeading._anchor_name(self.heading_indices.current)})'

    def link_to_top(self, top_level, sub_level):
        if top_level != 0 and self.heading_level > top_level:
            return f'[↖](#{MarkdownHeading._anchor_name(self.heading_indices.current[:top_level])})'
        else:
            return '[↖](#top)'

    def link_to_previous(self):
        return f'[↑](#{MarkdownHeading._anchor_name(self.heading_indices.previous)})' if self.heading_indices.previous else ''

    def link_to_next(self):
        return f'[↓](#{MarkdownHeading._anchor_name(self.heading_indices.next)})' if self.heading_indices.next else ''

    def to_markdown(self, with_anchor=False, top_level=0, sub_level=0, with_debug=False):
        result = []
        if with_anchor:
            result.append(self._complete_anchor())
        navigation_links_part = f'{self.link_to_top(top_level, sub_level)}{self.link_to_previous()}{self.link_to_next()} ' if with_anchor else ''
        debug_part = f'{self.heading_indices.current} ' if with_debug else ''
        result.append(f'{self.heading} {navigation_links_part}{debug_part}{self.text_after_heading}')
        return result


class MarkdownParser:
    REG_HEADING_CHAR = re.compile('^#+ .+')

    def _is_heading(self, line):
        return re.match(self.REG_HEADING_CHAR, line) is not None

    @staticmethod
    def _add_new_level(index):
        return (*index, 1)

    @staticmethod
    def _bump_last_level(index):
        return index[:-1] + (index[-1] + 1,)

    @staticmethod
    def _remove_obsolete_levels(index, current_level):
        return index[:current_level]

    def _generate_index(self, previous_index, current_header_level):
        assert current_header_level > 0
        previous_level = len(previous_index)
        if current_header_level > previous_level:
            return self._add_new_level(previous_index)
        elif current_header_level == previous_level:
            return self._bump_last_level(previous_index)
        else:
            shortened_index = self._remove_obsolete_levels(previous_index, current_header_level)
            return self._bump_last_level(shortened_index)

    def _set_next_index(self, lines):
        current_index = ()
        for heading in (heading for heading in reversed(lines) if isinstance(heading, MarkdownHeading)):
            next_index = heading.heading_indices.current
            heading.heading_indices = HeadingIndices(heading.heading_indices.previous, heading.heading_indices.current, current_index)
            current_index = next_index

    def _set_prev_and_current_index(self, lines):
        current_index = ()
        for heading in (heading for heading in lines if isinstance(heading, MarkdownHeading)):
            new_index = self._generate_index(current_index, heading.heading_level)
            heading.heading_indices = HeadingIndices(current_index, new_index, None)
            current_index = new_index

    def parse(self, lines):
        lines = [MarkdownHeading(line) if self._is_heading(line) else MarkdownLine(line) for line in lines]
        self._set_prev_and_current_index(lines)
        self._set_next_index(lines)
        return lines


class MarkdownDocument:
    REG_SPACER_BETWEEN_HEADER_AND_LINK = re.compile('(?<=#) (?=\\[)')
    REG_INTERNAL_ANCHOR = re.compile('<a.*name.*a>')
    REG_INTERNAL_LINK = re.compile('\\[.*\\]\\(#.*\\)')
    TOC_START = '<!-- toc_start -->'
    TOC_TOP_ANCHOR = '<a name="top"></a>'
    TOC_RULER = '---'
    TOC_EMPTY_LINE = ''
    TOC_END = '<!-- toc_end -->'

    def __init__(self, raw_lines, remove_old_toc=False):
        if remove_old_toc:
            raw_lines = list(self._cleansing_generator(raw_lines))
        self.md_lines = MarkdownParser().parse(raw_lines)

    @staticmethod
    def _cleansing_generator(lines):
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
    def _remove_existing_tocs(lines):
        try:
            while True:
                start = lines.index(MarkdownDocument.TOC_START)
                end = lines.index(MarkdownDocument.TOC_END)
                assert start < end
                if lines[start - 1] == MarkdownDocument.TOC_EMPTY_LINE:
                    start -= 1
                lines = [line for index, line in enumerate(lines) if not (start <= index <= end)]
        except ValueError:
            pass
        assert all(x not in [MarkdownDocument.TOC_START, MarkdownDocument.TOC_END] for x in lines)
        return lines

    def _create_toc(self, toc_parent_index, start_level, end_level):
        result = []
        parent_index_level = len(toc_parent_index)
        toc_lines = [line.to_toc_entry(parent_index_level) for line in self.md_lines if isinstance(line, MarkdownHeading) and self._is_line_in_toc(line, toc_parent_index, start_level, end_level)]
        if toc_lines:
            result.append(self.TOC_START)
            if parent_index_level == 0:
                result.append(self.TOC_TOP_ANCHOR)
                result.append(self.TOC_RULER)
            result.extend(toc_lines)
            if parent_index_level == 0:
                result.append(self.TOC_RULER)
            result.append(self.TOC_END)
        return result

    def _is_line_in_toc(self, line, toc_parent_index, start_level, end_level):
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
            lines.extend(self._create_toc((), 0, max_main_toc_level))
        for md_line in self.md_lines:
            with_anchor = self._needs_anchor(md_line, with_toc, max_main_toc_level, extra_sub_toc_level)
            lines.extend(md_line.to_markdown(with_anchor=with_anchor, top_level=max_main_toc_level, sub_level=extra_sub_toc_level, with_debug=with_debug))
            if self._should_insert_toc_here(with_toc, md_line, max_main_toc_level, max_main_toc_level + extra_sub_toc_level):
                lines.extend(self._create_toc(md_line.heading_indices.current, md_line.heading_level + 1, md_line.heading_level + extra_sub_toc_level))
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
