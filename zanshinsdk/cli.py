import sys
from collections import Iterable
from csv import writer
from enum import Enum
from json import dumps
from typing import Iterator, Dict, Any

import typer
from prettytable import PrettyTable

from zanshinsdk import Connection, __version__

app = typer.Typer()


class OutputFormat(Enum):
    """
    Used to specify command-line parameters indicating output format.
    """
    JSON = "json"
    TABLE = "table"
    CSV = "csv"
    HTML = "html"


class TyperWriter(object):
    """
    Workaround for use of csv.writer class, which expects a file-like object.
    """

    def write(self, line):
        typer.echo(line, nl=False)


def format_field(x: Any) -> str:
    """
    Function that formats a single field for output on a table or CSV output, in order to deal with nested arrays or objects in the JSON outputs of the API.
    :param x: the value to format
    :return: a string that is fit for console output
    """
    if x is None:
        return ""
    elif isinstance(x, (str, bytes)):
        return x
    elif isinstance(x, Iterable):
        ", ".join(map(format_field, x))
    elif isinstance(x, dict):
        return dumps(x)
    else:
        return str(x)


def output_iterable(iter: Iterator[Dict], format: OutputFormat) -> None:
    """
    Function that iterates over a series of dicts representing JSON objects returned by API list operations, and which
    outputs them using typer.echo in the specified format. Will use streaming processing for JSON and CSV formats,
    all others need to load all responses in memory in a PrettyTable prior to output, which could be problematic for
    things like alerts.
    :param iter: the iterator containing the JSON objects
    :param format: the output format to use
    :return: None
    """
    if format is OutputFormat.JSON:
        for entry in iter:
            typer.echo(dumps(entry, indent=4))
    elif format is OutputFormat.CSV:
        cw = writer(TyperWriter())
        field_names = None
        for entry in iter:
            if not field_names:
                field_names = sorted(entry.keys())
                cw.writerow(field_names)
            cw.writerow([format_field(entry.get(fn, None)) for fn in field_names])
    else:
        table = PrettyTable()
        for entry in iter:
            if not table.field_names:
                table.field_names = sorted(entry.keys())
            table.add_row([format_field(entry.get(fn, None)) for fn in table.field_names])
        if format is OutputFormat.TABLE:
            typer.echo(table.get_string())
        elif format is OutputFormat.JSON:
            typer.echo(table.get_json_string())
        elif format is OutputFormat.HTML:
            typer.echo(table.get_html_string())
        else:
            raise NotImplementedError("unexpected format type")


@app.command()
def me(profile: str = typer.Option("default",
                                   help="Configuration file section to use for credentials and other settings")):
    """
    Show details about the owner of the API key being used.
    """
    conn = Connection(profile=profile)
    typer.echo(dumps(conn.me(), indent=4))


@app.command()
def organizations(profile: str = typer.Option("default",
                                              help="Configuration file section to use for credentials and other settings"),
                  format: OutputFormat = typer.Option(OutputFormat.JSON.value, help="Format to use for the output.",
                                                      case_sensitive=False)):
    """
    Lists the organizations this user has direct access to as a member.
    """
    conn = Connection(profile=profile)
    output_iterable(conn.iter_organizations(), format)


@app.command()
def version():
    """
    Display the program and Python versions in use.
    """
    typer.echo(f'Zanshin Python SDK v{__version__}')
    typer.echo(f'Python {sys.version}')


if __name__ == "__main__":
    app()
