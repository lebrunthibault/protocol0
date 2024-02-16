from p0_backend.lib.abstract_cli import cli
import os

def delete_wav_aif_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".wav") or file.endswith(".aif") or file.endswith(".rx2"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


@cli.command(name="test")
async def command_test() -> None:
    folder_path = r"C:\Users\thiba\google_drive\music\vsts\Nerve\NerveData\Wav"
    delete_wav_aif_files(folder_path)


if __name__ == "__main__":
    cli()
