import re

PATH = '../tests/resources/simple.md'


class MarkdownLine:
    HEADER_CHAR = re.compile('^#*')

    def __init__(self, line, previous_index=None):
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
        check = re.search(MarkdownLine.HEADER_CHAR, line)
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
            return previous_index[:]

    @property
    def line(self):
        return self._line

    @property
    def index(self):
        return self._index


class MarkdownHelper:
    def __init__(self, path):
        self.path = path
        self.raw_content = self._read_from_file()
        self.md_content = self._convert_to_mdlines(self.raw_content)

    def _read_from_file(self):
        with open(self.path) as file:
            return file.readlines()

    def _convert_to_mdlines(self, lines):
        result = []
        current_index = []
        for line in lines:
            md_line = MarkdownLine(line=line.strip('\n'), previous_index=current_index)
            current_index = md_line.index
            result.append(md_line)
        return result

    def print(self):
        for md_line in self.md_content:
            print(md_line)


if __name__ == '__main__':
    MarkdownHelper(PATH).print()
