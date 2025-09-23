from p0_backend.lib.abstract_cli import cli
from p0_backend.settings import Settings


@cli.command(name="test")
async def command_test() -> None:
    settings = Settings()
    print(settings.ableton_version)


if __name__ == "__main__":
    cli()
