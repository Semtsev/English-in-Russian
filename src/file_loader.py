from pathlib import Path


def load_text(file_path: Path) -> str:
    """Читает текстовый файл в UTF-8."""
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")

    return file_path.read_text(encoding="utf-8-sig")