from p0_backend.lib.abstract_cli import cli


@cli.command(name="test")
async def command_test() -> None:
    import re

    log_file_path = r"C:\Users\thiba\AppData\Roaming\Ableton\Live 12.1.5\Preferences\Log.txt"
    regex = re.compile(r"AApplication: CommandLine : \"(.+\.als)\"")

    with open(log_file_path, "r", encoding="utf-8") as f:
        log_content = f.read()

    # 4. Find all matches of the .als path in the log.
    matches = regex.findall(log_content)

    if matches:
        # The last item in 'matches' is the most recent .als file mentioned.
        last_als_path = matches[-1]
        print("Last .als path found:", last_als_path)
    else:
        print("No .als file paths found in the log.")


if __name__ == "__main__":
    cli()
