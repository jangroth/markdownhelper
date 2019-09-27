import re


class MarkdownLine:
    REG_HEADER_CHAR = re.compile('^#*')

    def __init__(self, line, previous_index=[]):
        self._line = line
        self._index = self._generate_index(previous_index, line)

    def __str__(self):
        return f'{self._index} - {self._line}'

    def __eq__(self, other):
        if not isinstance(other, MarkdownLine):
            return NotImplemented
        return self._line == other._line and self._index == other._index

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self._line, self._index))

    @staticmethod
    def _get_header_level(line):
        check = re.search(MarkdownLine.REG_HEADER_CHAR, line)
        return check.span()[1] if check else 0

    @staticmethod
    def _add_new_level(index):
        return [*index, 1]

    @staticmethod
    def _bump_current_level(index):
        return index[:-1] + [(index[-1] + 1)]

    @staticmethod
    def _remove_current_and_bump_previous_level(index):
        return index[:-2] + [(index[-2] + 1)]

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
            return []

    def to_markdown(self, with_anchor=False, debug=False):
        top = f'\n[▲](#top)\n' if with_anchor and self.index else ''
        anchor = f'<a name="{self.anchor_name}"></a>\n' if with_anchor and self.index else ''
        debug = f'{self.index} - ' if debug and self.index else ''
        return f'{top}{anchor}{debug}{self.line}'

    def to_toc_entry(self):
        return f'{"  " * (len(self.index) - 1)}* [{self.line.partition(" ")[2]}](#{self.anchor_name})' if self.index else self.line

    @property
    def line(self):
        return self._line

    @property
    def index(self):
        return self._index

    @property
    def anchor_name(self):
        return '_'.join([str(i) for i in self._index])


class MarkdownDocument:
    REG_INTERNAL_ANCHOR = re.compile('<a.*name.*a>')
    REG_INTERNAL_LINK = re.compile('\\[.*\\]\\(#.*\\)')

    def __init__(self, raw_lines, strip_old_toc=False):
        cleansed_lines = self._raw_to_cleansed(raw_lines, strip_old_toc)
        self.md_lines = self._cleansed_to_md(cleansed_lines)

    def _raw_to_cleansed(self, lines, strip_old_toc=False):
        return list(self._cleansing_generator(lines, strip_old_toc))

    def _cleansing_generator(self, lines, strip_old_toc=False):
        for line in lines:
            line = line.strip('\n')
            if strip_old_toc and line:
                line = re.sub(self.REG_INTERNAL_ANCHOR, '', line)
                line = re.sub(self.REG_INTERNAL_LINK, '', line)
                if line:
                    yield line
            else:
                yield line

    def _cleansed_to_md(self, lines):
        result = []
        current_index = []
        for line in lines:
            md_line = MarkdownLine(line=line, previous_index=current_index)
            if md_line.index:
                current_index = md_line.index
            result.append(md_line)
        return result

    def dump(self, generate_toc=False, debug=False):
        if generate_toc:
            print('<a name="top"></a>')
            print('---')
            for line in self.md_lines:
                if line.index:
                    print(line.to_toc_entry())
            print('---')
        for md_line in self.md_lines:
            print(md_line.to_markdown(generate_toc, debug))


class MarkdownHelper:

    def __init__(self, path):
        self.raw_content = self._read_from_file(path)

    def _read_from_file(self, path):
        with open(path) as file:
            return file.readlines()

    def dump(self, generate_toc=False, strip_old_toc=False, debug=False):
        md_document = MarkdownDocument(self.raw_content, strip_old_toc)
        md_document.dump(generate_toc, debug)
