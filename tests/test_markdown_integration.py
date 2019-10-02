import os

import pytest

from markdown_helper import MarkdownHelper


@pytest.fixture
def mdh():
    return MarkdownHelper('resources/simple.md')


def test_should_add_and_remove_toc(mdh, capsys, tmp_path):
    mdh.dump()
    out1, _ = capsys.readouterr()
    path = os.path.join(tmp_path, 'simple_with_toc.md')
    with open(path, "w+") as testfile:
        testfile.write(out1)

    MarkdownHelper(path).dump()
    out2, _ = capsys.readouterr()

    assert out1 == out2
