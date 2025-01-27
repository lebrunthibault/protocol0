import re

from p0_backend.settings import Settings

settings = Settings()


def get_launched_set_path() -> str:
    with open(settings.log_file_path, "r", encoding="utf-8") as f:
        log_content = f.read()

    regex = re.compile(r"AApplication: CommandLine : \"(.+\.als)\"")
    matches = regex.findall(log_content)
    last_als_path = None

    if matches:
        # The last item in 'matches' is the most recent .als file mentioned.
        last_als_path = matches[-1]
        print("Last .als path found:", last_als_path)

    assert last_als_path, "No .als file paths found in the log."
    return last_als_path
