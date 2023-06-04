import requests

from p0_backend.settings import Settings
from p0_backend.lib.abstract_cli import cli


def update_set_title():
    requests.put(f"{Settings().http_api_url}/set", params={"title": "Dark Fantasy"})


@cli.command(name="test")
async def command_test() -> None:
    update_set_title()


if __name__ == "__main__":
    cli()
