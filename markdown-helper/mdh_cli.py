import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command()
@click.argument('path')
@click.option('--index/--no-index', default=False)
@click.option('--debug/--no-debug', default=False)
def dump(path, index, debug):
    MarkdownHelper(path=path).dump(generate_index=index, debug=debug)


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh()
