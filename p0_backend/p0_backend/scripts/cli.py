from p0_backend.lib.abstract_cli import cli


@cli.command(name="test")
async def command_test() -> None:
    pass


if __name__ == "__main__":
    cli()
