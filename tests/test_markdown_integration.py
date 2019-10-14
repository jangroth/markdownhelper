import os

import pytest
from markdown_helper import MarkdownHelper


@pytest.fixture
def mdh():
    return MarkdownHelper('tests/resources/simple.md')


def test_should_add_and_remove_toc(mdh, capsys, tmp_path):
    mdh.dump(add_toc=False)
    expected, _ = capsys.readouterr()
    mdh.dump(add_toc=True)
    out_with_toc, _ = capsys.readouterr()

    path = os.path.join(tmp_path, 'simple_with_toc.md')
    with open(path, "w+") as testfile:
        testfile.write(out_with_toc)

    MarkdownHelper(path).dump(remove_old_toc=True)
    result, _ = capsys.readouterr()

    assert result == expected