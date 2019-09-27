import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command()
@click.argument('path')
@click.option('--toc/--no-toc', default=False, help='Add toc')
@click.option('--remove-toc/--no-remove-toc', default=False, help='Remove old toc and internal links')
@click.option('--debug/--no-debug', default=False)
def dump(path, toc, debug):
    MarkdownHelper(path=path).dump(generate_toc=toc, debug=debug)


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh()
