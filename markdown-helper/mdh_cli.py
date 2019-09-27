import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command()
@click.argument('path')
@click.option('--toc/--no-toc', default=False, help='Add toc')
@click.option('--cleanse/--no-cleanse', default=False, help='Remove old toc and internal links')
@click.option('--debug/--no-debug', default=False)
def dump(path, toc, cleanse, debug):
    MarkdownHelper(path=path).dump(generate_toc=toc, strip_old_toc=cleanse, debug=debug)


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh()
