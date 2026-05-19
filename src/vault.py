from pathlib import Path
import tempfile
import atexit
import py7zr


ARCHIVE_PASSWORD = "12345"


class DataVault:
    def __init__(self, archive_name="data.7z"):
        self.base_dir = Path(__file__).resolve().parent.parent
        self.archive_path = self.base_dir / archive_name
        self.temp_dir_obj = None
        self.data_dir = None
        self.closed = False

    def open(self):
        self.temp_dir_obj = tempfile.TemporaryDirectory(prefix="app_data_")
        self.data_dir = Path(self.temp_dir_obj.name) / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if self.archive_path.exists():
            with py7zr.SevenZipFile(
                    self.archive_path,
                    mode="r",
                    password=ARCHIVE_PASSWORD
            ) as archive:
                archive.extractall(path=self.data_dir)

        nested_data_dir = self.data_dir / "data"
        if nested_data_dir.exists() and nested_data_dir.is_dir():
            self.data_dir = nested_data_dir

        print("XLSX FILES:", list(self.data_dir.rglob("*.xlsx")))

        atexit.register(self.close)
        return self.data_dir

    def close(self):
        if self.closed:
            return
        self.closed = True

        if self.data_dir and self.data_dir.exists():
            temp_archive = self.archive_path.with_suffix(".tmp.7z")

            if temp_archive.exists():
                temp_archive.unlink()

            with py7zr.SevenZipFile(
                    temp_archive,
                    mode="w",
                    password=ARCHIVE_PASSWORD
            ) as archive:
                for item in self.data_dir.rglob("*"):
                    if item.is_file():
                        archive.write(item, arcname=item.relative_to(self.data_dir))

            temp_archive.replace(self.archive_path)

        if self.temp_dir_obj is not None:
            self.temp_dir_obj.cleanup()



vault = DataVault()
DATA_DIR_OPEN = vault.open()