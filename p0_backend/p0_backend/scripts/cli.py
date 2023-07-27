from p0_backend.lib.abstract_cli import cli
from p0_backend.lib.notification.toast import show_notification


@cli.command(name="test")
async def command_test() -> None:
    show_notification("test")


if __name__ == "__main__":
    cli()
