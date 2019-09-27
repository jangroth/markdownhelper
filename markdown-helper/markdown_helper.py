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

    @property
    def line(self):
        return self._line

    @property
    def index(self):
        return self._index

    @property
    def anchor_name(self):
        return '_'.join([str(i) for i in self._index])


class MarkdownHelper:
    REG_INTERNAL_ANCHOR = re.compile('<a.*name.*a>')
    REG_INTERNAL_LINK = re.compile('\\[.*\\]\\(#.*\\)')

    def __init__(self, path):
        self.path = path
        self.raw_content = self._read_from_file()
        self.cleansed_content = self._raw_to_cleansed(self.raw_content)
        self.md_content = self._cleansed_to_md(self.cleansed_content)

    def _read_from_file(self):
        with open(self.path) as file:
            return file.readlines()

    def _raw_to_cleansed(self, lines):
        return list(self._cleansing_generator(lines))

    def _cleansing_generator(self, lines):
        for line in lines:
            line = line.strip('\n')
            if line:
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

    def _print_line(self, md_line, generate_anchors, debug):
        anchor = f'<a name="{md_line.anchor_name}"></a>\n' if generate_anchors and md_line.index else ''
        debug = f'{md_line.index} - ' if debug and md_line.index else ''
        print(f'{anchor}{debug}{md_line.line}')

    def _print_toc(self):
        print('---')
        for md_line in self.md_content:
            if md_line.index:
                print(f'{"  " * (len(md_line.index) - 1)}* [{md_line.line.partition(" ")[2]}](#{md_line.anchor_name})')
        print('---')

    def dump(self, generate_toc=False, debug=False):
        for md_line in self.md_content:
            self._print_line(md_line, generate_toc, debug)
        if generate_toc:
            self._print_toc()
