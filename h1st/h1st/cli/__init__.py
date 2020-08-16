import click
from .project import new_project_cli, new_model_cli


def main():
    """
    :meta private:
    """
    cli = click.Group()
    cli.add_command(new_project_cli)
    cli.add_command(new_model_cli)

    cli()
