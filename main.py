from pathlib import Path

from src.file_loader import load_text
from src.preprocessing import extract_comments
from src.normalization import normalize_text
from src.dictionary_matcher import load_dictionary, analyze_comments
from src.comparison import run_comparison

from src.file_saver import (
    save_comments_csv,
    save_comments_txt,
    save_detection_results,
    save_frequency_stats
)


# Корневая папка проекта
BASE_DIR = Path(__file__).resolve().parent

# Пути к папкам
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "processed"
DICTIONARY_FILE = BASE_DIR / "dictionary" / "anglicisms.csv"


def process_file(year: str, dictionary: list[dict]) -> None:
    """Обрабатывает комментарии за определённый год."""

    print(f"\n{'=' * 40}")
    print(f"Обработка данных за {year} год")
    print(f"{'=' * 40}")

    input_file = DATA_DIR / f"input{year}.txt"

    # 1. Чтение файла
    raw_text = load_text(input_file)

    # 2. Первичная очистка
    comments = extract_comments(raw_text)

    # 3. Нормализация
    normalized_comments = [
        normalize_text(comment)
        for comment in comments
    ]

    # 4. Сохранение очищенных комментариев
    save_comments_csv(
        comments,
        normalized_comments,
        OUTPUT_DIR / f"cleaned{year}.csv"
    )

    save_comments_txt(
        comments,
        OUTPUT_DIR / f"cleaned{year}.txt"
    )

    # 5. Поиск англицизмов и подсчёт частоты
    detected, statistics = analyze_comments(
        comments,
        normalized_comments,
        dictionary
    )

    # 6. Сохранение результатов
    save_detection_results(
        detected,
        OUTPUT_DIR / f"detected{year}.csv"
    )

    save_frequency_stats(
        statistics,
        OUTPUT_DIR / f"frequency{year}.csv"
    )

    # 7. Вывод результатов в консоль
    total_occurrences = sum(
        item["occurrences"] for item in statistics
    )

    print(f"Всего комментариев: {len(comments)}")
    print(f"Комментариев с англицизмами: {len(detected)}")
    print(f"Всего обнаруженных употреблений: {total_occurrences}")

    print("\nТоп-10 англицизмов:")

    for item in statistics[:10]:
        if item["occurrences"] > 0:
            print(
                f"{item['word']}: "
                f"{item['occurrences']} употреблений"
            )


def main() -> None:
    """Главная функция программы."""

    print("Анализ англицизмов в комментариях")

    dictionary = load_dictionary(DICTIONARY_FILE)

    print(f"Загружено словарных записей: {len(dictionary)}")

    for year in ["2017", "2021", "2026"]:
        try:
            process_file(year, dictionary)

        except FileNotFoundError as error:
            print(f"Ошибка: {error}")

    # После обработки всех файлов запускаем сравнение
    try:
        run_comparison()

    except FileNotFoundError as error:
        print(f"Ошибка сравнительного анализа: {error}")


if __name__ == "__main__":
    main()
