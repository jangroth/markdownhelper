import re
from collections import namedtuple

PATH = '/home/jan/Projects/test/markdown.md'
HEADER_CHAR = re.compile('^#*')

MarkdownLine = namedtuple('MarkdownLine', 'index line')


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
        last_index = []
        for line in lines:
            line = line.strip('\n')
            last_index, md_line = self._get_markdown_line(last_index, line)
            result.append(md_line)
        return result

    def _get_header_level(self, line):
        check = re.search(HEADER_CHAR, line)

        return check.span()[1] if check else 0

    def _get_markdown_line(self, last_index, line):
        new_index = last_index
        last_level = len(last_index)
        current_level = self._get_header_level(line)
        if current_level:
            if current_level > last_level:
                new_index.append(1)
            elif current_level == last_level:
                last_index_of_this_level = last_index[-1]
                new_index = last_index[0:current_level - 1]
                new_index.append(last_index_of_this_level + 1)
            elif current_level < last_level:
                last_index_of_previous_level = last_index[-2]
                new_index = last_index[0:current_level - 1]
                new_index.append(last_index_of_previous_level + 1)

        return new_index, MarkdownLine(new_index, line)

    def print(self):
        for md_line in self.md_content:
            print(md_line)


if __name__ == '__main__':
    MarkdownHelper(PATH).print()
