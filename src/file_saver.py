import csv
from pathlib import Path


def save_comments_csv(
    comments: list[str],
    normalized_comments: list[str],
    file_path: Path
) -> None:
    """Сохраняет исходные и нормализованные комментарии в CSV."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "comment_id",
            "original_text",
            "normalized_text"
        ])

        for comment_id, (original, normalized) in enumerate(
            zip(comments, normalized_comments),
            start=1
        ):
            writer.writerow([
                comment_id,
                original,
                normalized
            ])


def save_comments_txt(comments: list[str], file_path: Path) -> None:
    """Сохраняет комментарии по одному на строку."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(
        "\n".join(comments),
        encoding="utf-8"
    )

def save_detection_results(
    results: list[dict],
    file_path: Path
) -> None:
    """Сохраняет комментарии, в которых найдены англицизмы."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        fields = [
            "comment_id",
            "original_text",
            "normalized_text",
            "found_anglicisms"
        ]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)


def save_frequency_stats(
    statistics: list[dict],
    file_path: Path
) -> None:
    """Сохраняет статистику употребления англицизмов."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with file_path.open("w", encoding="utf-8-sig", newline="") as file:
        fields = [
            "word",
            "category",
            "occurrences",
            "comments_count"
        ]

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(statistics)