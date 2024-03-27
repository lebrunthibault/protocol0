from p0_backend.lib.abstract_cli import cli
import os


@cli.command(name="test")
async def command_test() -> None:
    directory = (
        r"C:\Users\thiba\OneDrive\Documents\Xfer\Serum Presets\Presets\Audio Imperia Polaris"
    )

    # Function to rename files
    def rename_files(dir):
        for filename in os.listdir(dir):
            substring = "audioimperia_polaris_serum_"
            if substring in filename:
                new_filename = filename.replace(substring, "").replace("_", " ").title()

                # Construct the full path for the old and new filenames
                old_filepath = os.path.join(dir, filename)
                new_filepath = os.path.join(dir, new_filename)

                # Rename the file
                os.rename(old_filepath, new_filepath)
                print(f"Renamed: {old_filepath} -> {new_filepath}")

    # Call the function to rename files
    rename_files(directory)


if __name__ == "__main__":
    cli()
