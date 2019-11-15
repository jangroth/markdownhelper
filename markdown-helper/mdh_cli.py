import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command(help='Dumps markdown document to console')
@click.argument('path')
@click.option('--debug/--no-debug', default=False, help='Displays debug information')
def dump(path, debug):
    MarkdownHelper(path=path).dump(add_toc=False, remove_old_toc=False, with_debug=debug)


@click.command(help='Removes existing TOC and all internal links')
@click.argument('path')
def cleanse(path):
    MarkdownHelper(path=path).cleanse()


@click.command(help='Adds TOC to top of file')
@click.argument('path')
@click.option('--max-level', default=0, help='Only go max-levels deep. Leave empty or zero for all levels.')
@click.option('--navigation/--no-navigation', default=False, help='Adds navigation links to headers')
def toc(path, max_level, navigation):
    MarkdownHelper(path=path).add_toc(add_navigation=navigation, max_level=max_level)


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh.add_command(cleanse)
    mdh.add_command(toc)
    mdh()
