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


@app.command()
def list_alerts(organization_id: str,
                scan_target_id: str = typer.Argument(
                    None, help="Scan target Id that generated this alerts"),
                following_id: str = typer.Argument(
                    None, help="Organization Id that is followed"),
                state: str = typer.Argument(
                    None, help="Current Alert State. Options are [\"OPEN\" \"ACTIVE\" \"IN_PROGRESS\" \"RISK_ACCEPTED\" \"RESOLVED\" \"CLOSED\"]"),
                severity: str = typer.Argument(
                    None, help="Current Alert Severity. Options are [\"CRITICAL\" \"HIGH\" \"MEDIUM\" \"LOW\" \"INFO\"]"),
                tag: str = typer.Argument(
                    None, help="Alerts with given Tags"),
                page: int = 1,
                size: int = 1000,
                profile: str = typer.Option("default",
                                            help="Configuration file section to use for credentials and other settings")):
    """
    Display alerts by page, filtering by organization_id.

    Parameters
    ----------
    organization_id : str
        UUID that represents the organization that owns the alerts
    scan_target_id : str, optional
        UUID that represents the scan target that generated the alerts
    following_id : str, optional
        Organization UUID that is followed
    state : str, optional
        Alert State, can be OPEN, ACTIVE, IN_PROGRESS, RISK_ACCEPTED, RESOLVED, or CLOSED
    severity : str, optional
        Alert Severity, can be CRITICAL, HIGH, MEDIUM, LOW, or INFO
    tag : str, optional
        Alerts that contain given tag
    page : int, optional, default 1
        Page number of the query
    size : int, optional, default 1000
        Number of alerts returned by each page
    profile : string, optional, default \"default\"
        Profile defined in the config file
    """
    if not organization_id:
        return
    conn = Connection(profile=profile)
    typer.echo(dumps(conn.list_alerts(
        organization_id=organization_id,
        scan_target_id=scan_target_id,
        following_id=following_id,
        state=state,
        severity=severity,
        tag=tag,
        page=page,
        size=size), indent=4))

if __name__ == "__main__":
    app()
