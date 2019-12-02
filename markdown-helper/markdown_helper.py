import re


class MarkdownLine:
    REG_HEADER_CHAR = re.compile('^#*')

    def __init__(self, line, previous_index=(), next_index=()):
        self._line = line
        self._current_index = self._generate_index(previous_index, line)
        self._previous_index = previous_index
        self._next_index = next_index

    def __str__(self):
        return f'{self._current_index}:{self._line}'

    def __repr__(self):
        return f'MarkdownLine(line={self.line}, previous_index={self._previous_index}, next_index={self._next_index})'

    def __eq__(self, other):
        if not isinstance(other, MarkdownLine):
            return NotImplemented
        return self._line == other._line and self._current_index == other._current_index

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self._line, self._current_index))

    @staticmethod
    def _get_header_level(line):
        check = re.search(MarkdownLine.REG_HEADER_CHAR, line)
        return check.span()[1] if check else 0

    def _generate_index(self, previous_index, line):
        previous_level = len(previous_index)
        current_level = self._get_header_level(line)
        if current_level:
            if current_level > previous_level:
                return self._add_new_level(previous_index)
            elif current_level == previous_level:
                return self._bump_current_level(previous_index)
            elif current_level < previous_level:
                return self._remove_current_and_bump_previous_level(previous_index)
        else:
            return ()

    @staticmethod
    def _add_new_level(index):
        return (*index, 1)

    @staticmethod
    def _bump_current_level(index):
        return index[:-1] + (index[-1] + 1,)

    @staticmethod
    def _remove_current_and_bump_previous_level(index):
        return index[:-2] + (index[-2] + 1,)

    @staticmethod
    def _to_anchor_name(index):
        return '_'.join([str(i) for i in index])

    def set_next_index(self, next_index):
        self._next_index = next_index

    def to_markdown(self, with_anchor=False, with_navigation=False, with_debug=False):
        if with_anchor and self.index:
            pre_line = f'<a name="{self.anchor_name}"></a>'
            line = '#' * len(self.index)
            if with_navigation:
                line += ' '
                line += self.link_to_top
                line += self.link_to_previous
                line += self.link_to_next
            line += f'{self.index} - ' if with_debug else ''
            line += ' ' + self.line.partition(" ")[2]
            return [pre_line, line]
        else:
            return [self.line]

    def to_toc_entry(self):
        return f'{"  " * (len(self.index) - 1)}* [{self.line.partition(" ")[2]}](#{self._to_anchor_name(self._current_index)})' if self.index else self.line

    @property
    def line(self):
        return self._line

    @property
    def index(self):
        return self._current_index

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


class MarkdownDocument:
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
            start = lines.index('[toc_start]::')
            end = lines.index('[toc_end]::')
            if lines[start - 1] == '' and lines[end - 1] == '':
                lines = [line for index, line in enumerate(lines) if index < start - 1 or index > end]
        except ValueError:
            pass
        return lines

    @staticmethod
    def _cleansed_to_md(lines):
        result = []
        current_index = ()
        for line in lines:
            md_line = MarkdownLine(line=line, previous_index=current_index)
            if md_line.index:
                current_index = md_line.index
            result.append(md_line)
        return result

    @staticmethod
    def _add_next_indices_to_md(md_lines):
        result = []
        current_index = ()
        for line in reversed(md_lines):
            if line.index:
                line.set_next_index(current_index)
                current_index = line.index
            result.append(line)
        return result[::-1]

    @staticmethod
    def _should_print_toc_line(line, max_level):
        result = False
        if line.index:
            if max_level == 0 or len(line.index) <= max_level:
                result = True
        return result

    def dump(self, add_toc=False, add_navigation=False, max_level=0, with_debug=False):
        lines = []
        if add_toc:
            lines.append(self.TOC_START)
            for line in self.md_lines:
                if self._should_print_toc_line(line, max_level):
                    lines.append(line.to_toc_entry())
            lines.append(self.TOC_END)
        for md_line in self.md_lines:
            lines.append(md_line.to_markdown(with_anchor=add_toc, with_navigation=add_navigation, with_debug=with_debug))


class MarkdownHelper:

    def __init__(self, path):
        self.raw_content = self._read_from_file(path)

    @staticmethod
    def _read_from_file(path):
        with open(path) as file:
            return [line.rstrip('\n') for line in file]

    def dump(self, add_toc=False, remove_old_toc=False, with_debug=False):
        md_document = MarkdownDocument(lines=self.raw_content, remove_old_toc=remove_old_toc)
        md_document.dump(add_toc=add_toc, with_debug=with_debug)

    def cleanse(self):
        md_document = MarkdownDocument(lines=self.raw_content, remove_old_toc=True)
        md_document.dump()

    def add_toc(self, add_navigation=False, max_level=0):
        md_document = MarkdownDocument(lines=self.raw_content)
        md_document.dump(add_toc=True, add_navigation=add_navigation, max_level=max_level)
