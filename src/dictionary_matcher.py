import csv
import re
from pathlib import Path

from src.normalization import normalize_text


def load_dictionary(file_path: Path) -> list[dict]:
    """Загружает словарь англицизмов из CSV."""

    dictionary = []

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            word = row["word"].strip()
            category = row["category"].strip()

            # Основное слово и его варианты
            variants = [word]

            if row.get("variants"):
                variants.extend(
                    variant.strip()
                    for variant in row["variants"].split(";")
                    if variant.strip()
                )

            # Нормализуем варианты так же, как комментарии
            normalized_variants = {
                normalize_text(variant)
                for variant in variants
            }

            normalized_variants.discard("")

            dictionary.append({
                "word": word,
                "category": category,
                "variants": normalized_variants
            })

    return dictionary


def find_anglicisms(
    text: str,
    dictionary: list[dict]
) -> dict[str, int]:
    """Находит англицизмы в одном нормализованном комментарии."""

    found = {}

    for entry in dictionary:
        positions = set()

        for variant in entry["variants"]:
            # Ищем целые слова или фразы, а не части других слов
            pattern = (
                r"(?<!\w)"
                + r"\s+".join(re.escape(part) for part in variant.split())
                + r"(?!\w)"
            )

            for match in re.finditer(pattern, text):
                positions.add((match.start(), match.end()))

        if positions:
            found[entry["word"]] = len(positions)

    return found


def analyze_comments(
    comments: list[str],
    normalized_comments: list[str],
    dictionary: list[dict]
) -> tuple[list[dict], list[dict]]:
    """Ищет англицизмы и рассчитывает статистику."""

    statistics = {}

    # Изначально добавляем все слова словаря, даже если они не встретились
    for entry in dictionary:
        statistics[entry["word"]] = {
            "word": entry["word"],
            "category": entry["category"],
            "occurrences": 0,
            "comments_count": 0
        }

    detected_comments = []

    for comment_id, (original, normalized) in enumerate(
        zip(comments, normalized_comments),
        start=1
    ):
        found = find_anglicisms(normalized, dictionary)

        if found:
            detected_comments.append({
                "comment_id": comment_id,
                "original_text": original,
                "normalized_text": normalized,
                "found_anglicisms": "; ".join(found.keys())
            })

        for word, count in found.items():
            statistics[word]["occurrences"] += count
            statistics[word]["comments_count"] += 1

    frequency = list(statistics.values())

    frequency.sort(
        key=lambda item: item["occurrences"],
        reverse=True
    )

    return detected_comments, frequency