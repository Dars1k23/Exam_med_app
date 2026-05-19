from pathlib import Path
import py7zr

ARCHIVE_PASSWORD = "12345"
source_dir = Path("data")
archive_path = Path("data.7z")

if not source_dir.exists():
    raise FileNotFoundError(f"Папка не найдена: {source_dir}")

with py7zr.SevenZipFile(archive_path, "w", password=ARCHIVE_PASSWORD) as archive:
    for item in source_dir.rglob("*"):
        archive.write(item, arcname=item.relative_to(source_dir))

print(f"Архив создан: {archive_path.resolve()}")