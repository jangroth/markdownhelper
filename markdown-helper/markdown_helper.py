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

    def to_markdown(self, with_anchor=False, debug=False):
        if self.index:
            prefix = f'<a name="{self.anchor_name}"></a>\n' if with_anchor else ''
            prefix += '#' * len(self.index)
            prefix += ' '
            prefix += self.link_to_top
            prefix += self.link_to_previous
            prefix += self.link_to_next
            prefix += f'{self.index} - ' if debug else ''
            prefix += ' ' + self.line.partition(" ")[2]
            return prefix
        else:
            return self.line

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

    def __init__(self, lines, strip_old_toc=False):
        if strip_old_toc:
            lines = list(self._cleansing_generator(lines))
        md_lines_with_previous_index = self._cleansed_to_md(lines)
        self.md_lines = self._add_next_indices_to_md(md_lines_with_previous_index)

    def _cleansing_generator(self, lines):
        lines = self._remove_old_toc(lines)
        for line in lines:
            line = re.sub(self.REG_SPACER_BETWEEN_HEADER_AND_LINK, '', line)
            line = re.sub(self.REG_INTERNAL_ANCHOR, '', line)
            line = re.sub(self.REG_INTERNAL_LINK, '', line)
            if line:
                yield line

    def _remove_old_toc(self, lines):
        try:
            start = lines.index('[toc_start]::')
            end = lines.index('[toc_end]::')
            if lines[start - 1] == '' and lines[end - 1] == '':
                lines = [line for index, line in enumerate(lines) if index < start - 1 or index > end]
        except ValueError:
            pass
        return lines

    def _cleansed_to_md(self, lines):
        result = []
        current_index = ()
        for line in lines:
            md_line = MarkdownLine(line=line, previous_index=current_index)
            if md_line.index:
                current_index = md_line.index
            result.append(md_line)
        return result

    def _add_next_indices_to_md(self, md_lines):
        result = []
        current_index = ()
        for line in reversed(md_lines):
            if line.index:
                line.set_next_index(current_index)
                current_index = line.index
            result.append(line)
        return result[::-1]

    def dump(self, generate_toc=False, debug=False):
        if generate_toc:
            print('\n[toc_start]::')
            print('<a name="top"></a>')
            print('---')
            for line in self.md_lines:
                if line.index:
                    print(line.to_toc_entry())
            print('---')
            print('\n[toc_end]::')
        for md_line in self.md_lines:
            print(md_line.to_markdown(generate_toc, debug))


class MarkdownHelper:

    def __init__(self, path):
        self.raw_content = self._read_from_file(path)

    @staticmethod
    def _read_from_file(path):
        with open(path) as file:
            return [line.rstrip('\n') for line in file]

    def dump(self, generate_toc=False, strip_old_toc=False, debug=False):
        md_document = MarkdownDocument(self.raw_content, strip_old_toc)
        md_document.dump(generate_toc, debug)
