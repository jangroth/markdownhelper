import os

import pytest

from markdown_helper import MarkdownHelper


@pytest.fixture
def mdh():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    test_file = os.path.join(current_dir, '..', 'resources', 'simple.md')
    return MarkdownHelper(test_file)


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
