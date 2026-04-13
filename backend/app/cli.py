from uuid import UUID

import typer

from app.db.session import SessionLocal
from app.schemas.engagement import EngagementCreate
from app.schemas.scan import ScanCreate
from app.services.auth_service import create_user
from app.services.engagement_service import create_engagement
from app.services.scan_service import create_scan

cli = typer.Typer(no_args_is_help=True)


@cli.command("create-user")
def create_user_command(email: str, password: str, role: str = "user") -> None:
    with SessionLocal() as db:
        user = create_user(db, email=email, password=password, role=role)
        typer.echo(f"Created user {user.email} ({user.role.value})")


@cli.command("create-engagement")
def create_engagement_command(user_email: str, name: str, scope: str, description: str = "") -> None:
    from app.services.auth_service import get_user_by_email

    with SessionLocal() as db:
        user = get_user_by_email(db, user_email)
        if not user:
            raise typer.Exit(code=1)
        engagement = create_engagement(
            db,
            EngagementCreate(name=name, description=description, scope=[item.strip() for item in scope.split(",")], approval_mode=True),
            user,
        )
        typer.echo(f"Created engagement {engagement.id}")


@cli.command("create-scan")
def create_scan_command(user_email: str, engagement_id: UUID, target: str, attestation: str) -> None:
    from app.services.auth_service import get_user_by_email

    with SessionLocal() as db:
        user = get_user_by_email(db, user_email)
        if not user:
            raise typer.Exit(code=1)
        scan = create_scan(
            db,
            ScanCreate(engagement_id=engagement_id, target=target, human_in_the_loop=True, attestation=attestation),
            user,
        )
        typer.echo(f"Created scan {scan.id}")


def main() -> None:
    cli()
