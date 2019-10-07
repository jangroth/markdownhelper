import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command(help='Dumps markdown document to console')
@click.argument('path')
@click.option('--debug/--no-debug', default=False, help='Displays debug information')
def dump(path, debug):
    MarkdownHelper(path=path).dump(generate_toc=False, strip_old_toc=False, debug=debug)


@click.command(help='Removes existing TOC and all internal links')
@click.argument('path')
def cleanse(path):
    MarkdownHelper(path=path).cleanse()


@click.command(help='Adds TOC to top of file')
@click.argument('path')
def toc(path):
    MarkdownHelper(path=path).add_toc()


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh.add_command(cleanse)
    mdh.add_command(toc)
    mdh()
