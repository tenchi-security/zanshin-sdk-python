import sys
from json import dumps

import typer

from zanshinsdk import Connection, __version__

app = typer.Typer()


@app.command()
def me(profile: str = typer.Option("default",
                                   help="Configuration file section to use for credentials and other settings")):
    """
    Show details about the owner of the API key being used.
    """
    conn = Connection(profile=profile)
    typer.echo(dumps(conn.me(), indent=4))


@app.command()
def version():
    """
    Display the SDK and CLI version.
    """
    typer.echo(f'Zanshin Python SDK v{__version__}')
    typer.echo(f'Python {sys.version}')


if __name__ == "__main__":
    app()
