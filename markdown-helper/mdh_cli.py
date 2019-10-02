import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command(help='Dump markdown document. Use option flags to add or remove TOC.')
@click.argument('path')
@click.option('--toc/--no-toc', default=False, help='Add toc to document')
@click.option('--cleanse/--no-cleanse', default=False, help='Remove old toc and all internal links & anchors')
@click.option('--debug/--no-debug', default=False, help='Display debug information')
def dump(path, toc, cleanse, debug):
    MarkdownHelper(path=path).dump(generate_toc=toc, strip_old_toc=cleanse, debug=debug)


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh()
