import click

from markdown_helper import MarkdownHelper


@click.group()
def mdh():
    pass


@click.command()
@click.argument('path')
def dump(path):
    MarkdownHelper(path=path).print()


if __name__ == '__main__':
    mdh.add_command(dump)
    mdh()
