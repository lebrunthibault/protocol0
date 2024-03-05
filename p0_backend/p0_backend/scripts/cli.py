from p0_backend.lib.abstract_cli import cli
import os


@cli.command(name="test")
async def command_test() -> None:
    directory = r"D:\ableton projects\tracks\Ay Soare\mastering stems"

    # Function to rename files
    def rename_files(directory):
        for filename in os.listdir(directory):
            prefix = "mix "
            if filename.startswith(prefix):
                new_filename = filename[len(prefix) :]

                # Construct the full path for the old and new filenames
                old_filepath = os.path.join(directory, filename)
                new_filepath = os.path.join(directory, new_filename)

                # Rename the file
                os.rename(old_filepath, new_filepath)
                print(f"Renamed: {old_filepath} -> {new_filepath}")

    # Call the function to rename files
    rename_files(directory)


if __name__ == "__main__":
    cli()
