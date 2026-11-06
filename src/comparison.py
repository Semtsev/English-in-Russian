
import csv
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
RESULTS_DIR = BASE_DIR / "results"
CHARTS_DIR = RESULTS_DIR / "charts"
TABLES_DIR = RESULTS_DIR / "tables"

YEARS = ["2017", "2021", "2026"]

# Количество слов для графика наиболее популярных англицизмов
TOP_WORDS = 15

# Количество категорий для отдельного графика
TOP_CATEGORIES = 10


def prepare_directories():
    """Создаёт папки для таблиц и графиков."""

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(file_path: Path) -> pd.DataFrame:
    """Загружает CSV-файл."""

    if not file_path.exists():
        raise FileNotFoundError(f"Не найден файл: {file_path}")

    return pd.read_csv(file_path, encoding="utf-8-sig")


def load_year_data(year: str) -> dict:
    """Загружает и рассчитывает показатели за один год."""

    comments = load_csv(DATA_DIR / f"cleaned{year}.csv")
    detected = load_csv(DATA_DIR / f"detected{year}.csv")
    frequency = load_csv(DATA_DIR / f"frequency{year}.csv")

    # Общее количество комментариев
    total_comments = len(comments)

    # Количество комментариев с англицизмами
    comments_with_anglicisms = len(detected)

    # Общее количество слов в корпусе
    total_words = (
        comments["normalized_text"]
        .fillna("")
        .astype(str)
        .str.split()
        .str.len()
        .sum()
    )

    # Общее количество употреблений англицизмов
    total_occurrences = pd.to_numeric(
        frequency["occurrences"],
        errors="coerce"
    ).fillna(0).sum()

    # Доля комментариев с англицизмами
    comments_percentage = (
        comments_with_anglicisms / total_comments * 100
        if total_comments else 0
    )

    # Частота англицизмов на 1000 слов
    frequency_per_1000 = (
        total_occurrences / total_words * 1000
        if total_words else 0
    )

    # Частота англицизмов на 100 комментариев
    occurrences_per_100_comments = (
        total_occurrences / total_comments * 100
        if total_comments else 0
    )

    return {
        "year": year,
        "total_comments": total_comments,
        "comments_with_anglicisms": comments_with_anglicisms,
        "comments_percentage": comments_percentage,
        "total_words": int(total_words),
        "total_occurrences": int(total_occurrences),
        "frequency_per_1000_words": frequency_per_1000,
        "occurrences_per_100_comments": occurrences_per_100_comments,
        "frequency": frequency
    }


def build_general_statistics(year_data: list[dict]) -> pd.DataFrame:
    """Формирует общую сравнительную таблицу."""

    rows = []

    for data in year_data:
        rows.append({
            "year": data["year"],
            "total_comments": data["total_comments"],
            "comments_with_anglicisms": data["comments_with_anglicisms"],
            "comments_percentage": round(
                data["comments_percentage"], 2
            ),
            "total_words": data["total_words"],
            "total_occurrences": data["total_occurrences"],
            "frequency_per_1000_words": round(
                data["frequency_per_1000_words"], 3
            ),
            "occurrences_per_100_comments": round(
                data["occurrences_per_100_comments"], 2
            )
        })

    return pd.DataFrame(rows)


def build_word_dynamics(year_data: list[dict]) -> pd.DataFrame:
    """Формирует таблицу динамики каждого англицизма."""

    all_words = set()

    for data in year_data:
        all_words.update(data["frequency"]["word"].dropna().astype(str))

    rows = []

    for word in sorted(all_words):

        row = {"word": word}

        for data in year_data:
            frequency = data["frequency"]

            matches = frequency[
                frequency["word"].astype(str) == word
            ]

            occurrences = (
                pd.to_numeric(matches["occurrences"], errors="coerce")
                .fillna(0)
                .sum()
            )

            rate = (
                occurrences / data["total_words"] * 1000
                if data["total_words"] else 0
            )

            row[f"{data['year']}_occurrences"] = int(occurrences)
            row[f"{data['year']}_per_1000_words"] = round(rate, 4)

        rows.append(row)

    return pd.DataFrame(rows)


def build_category_dynamics(year_data: list[dict]) -> pd.DataFrame:
    """Формирует таблицу динамики категорий англицизмов."""

    all_categories = set()

    for data in year_data:
        all_categories.update(
            data["frequency"]["category"].dropna().astype(str)
        )

    rows = []

    for category in sorted(all_categories):

        row = {"category": category}

        for data in year_data:
            frequency = data["frequency"]

            matches = frequency[
                frequency["category"].astype(str) == category
            ]

            occurrences = (
                pd.to_numeric(matches["occurrences"], errors="coerce")
                .fillna(0)
                .sum()
            )

            rate = (
                occurrences / data["total_words"] * 1000
                if data["total_words"] else 0
            )

            row[f"{data['year']}_occurrences"] = int(occurrences)
            row[f"{data['year']}_per_1000_words"] = round(rate, 4)

        rows.append(row)

    return pd.DataFrame(rows)


def configure_plots():
    """Настраивает внешний вид графиков и поддержку кириллицы."""

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [
        "Arial",
        "DejaVu Sans",
        "Liberation Sans"
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.figsize"] = (11, 6)
    plt.rcParams["figure.dpi"] = 120


def save_plot(filename: str):
    """Сохраняет текущий график."""

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()


def plot_total_occurrences(general: pd.DataFrame):
    """График 1. Абсолютное количество употреблений."""

    plt.figure()

    plt.bar(
        general["year"],
        general["total_occurrences"]
    )

    plt.title("Количество употреблений англицизмов по годам")
    plt.xlabel("Год")
    plt.ylabel("Количество употреблений")
    plt.grid(axis="y", alpha=0.3)

    save_plot("01_total_occurrences.png")


def plot_frequency_per_1000(general: pd.DataFrame):
    """График 2. Частота англицизмов на 1000 слов."""

    plt.figure()

    plt.plot(
        general["year"],
        general["frequency_per_1000_words"],
        marker="o",
        linewidth=2
    )

    plt.title("Частота англицизмов на 1000 слов по годам")
    plt.xlabel("Год")
    plt.ylabel("Употреблений на 1000 слов")
    plt.grid(alpha=0.3)

    save_plot("02_frequency_per_1000_words.png")


def plot_comments_percentage(general: pd.DataFrame):
    """График 3. Доля комментариев с англицизмами."""

    plt.figure()

    plt.bar(
        general["year"],
        general["comments_percentage"]
    )

    plt.title("Доля комментариев, содержащих англицизмы")
    plt.xlabel("Год")
    plt.ylabel("Доля комментариев, %")
    plt.ylim(bottom=0)
    plt.grid(axis="y", alpha=0.3)

    save_plot("03_comments_percentage.png")


def plot_top_words(word_dynamics: pd.DataFrame):
    """График 4. Самые популярные англицизмы."""

    if word_dynamics.empty:
        return

    columns = [
        f"{year}_per_1000_words"
        for year in YEARS
    ]

    # Отбираем 15 слов с наибольшей суммарной
    # нормализованной частотой за все годы
    word_dynamics = word_dynamics.copy()

    word_dynamics["total_rate"] = word_dynamics[columns].sum(axis=1)

    top = word_dynamics.nlargest(TOP_WORDS, "total_rate")

    plot_data = top.set_index("word")[columns]
    plot_data.columns = YEARS

    ax = plot_data.plot(kind="bar", figsize=(13, 7))

    ax.set_title("Популярность отдельных англицизмов")
    ax.set_xlabel("Англицизм")
    ax.set_ylabel("Употреблений на 1000 слов")
    ax.legend(title="Год")
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=45, ha="right")

    save_plot("04_top_anglicisms.png")


def plot_category_share(category_dynamics: pd.DataFrame):
    """График 5. Доля категорий в общем числе англицизмов."""

    if category_dynamics.empty:
        return

    occurrence_columns = [
        f"{year}_occurrences"
        for year in YEARS
    ]

    data = category_dynamics.set_index("category")[occurrence_columns].copy()
    data.columns = YEARS

    # Переводим количество употреблений в проценты
    percentages = data.div(data.sum(axis=0).replace(0, 1), axis=1) * 100

    # Оставляем наиболее распространённые категории,
    # остальные объединяем в категорию «Другие»
    totals = data.sum(axis=1)
    top_categories = totals.nlargest(TOP_CATEGORIES).index

    selected = percentages.loc[
        percentages.index.isin(top_categories)
    ].copy()

    other = percentages.loc[
        ~percentages.index.isin(top_categories)
    ].sum(axis=0)

    if not other.empty and other.sum() > 0:
        selected.loc["Другие"] = other

    ax = selected.T.plot(
        kind="bar",
        stacked=True,
        figsize=(12, 7)
    )

    ax.set_title("Структура англицизмов по категориям")
    ax.set_xlabel("Год")
    ax.set_ylabel("Доля категории, %")
    ax.legend(title="Категория", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.grid(axis="y", alpha=0.3)

    save_plot("05_category_share.png")


def plot_top_categories(category_dynamics: pd.DataFrame):
    """График 6. Частота категорий на 1000 слов."""

    if category_dynamics.empty:
        return

    columns = [
        f"{year}_per_1000_words"
        for year in YEARS
    ]

    data = category_dynamics.copy()
    data["total_rate"] = data[columns].sum(axis=1)

    top = data.nlargest(TOP_CATEGORIES, "total_rate")

    plot_data = top.set_index("category")[columns]
    plot_data.columns = YEARS

    ax = plot_data.plot(kind="bar", figsize=(13, 7))

    ax.set_title("Частота категорий англицизмов по годам")
    ax.set_xlabel("Категория")
    ax.set_ylabel("Употреблений на 1000 слов")
    ax.legend(title="Год")
    ax.grid(axis="y", alpha=0.3)

    plt.xticks(rotation=45, ha="right")

    save_plot("06_category_frequency.png")


def run_comparison():
    """Запускает полный сравнительный анализ."""

    print("\n" + "=" * 50)
    print("СРАВНИТЕЛЬНЫЙ АНАЛИЗ АНГЛИЦИЗМОВ")
    print("=" * 50)

    prepare_directories()
    configure_plots()

    year_data = []

    for year in YEARS:
        print(f"Загрузка данных за {year} год...")
        year_data.append(load_year_data(year))

    # Создание сравнительных таблиц
    general = build_general_statistics(year_data)
    words = build_word_dynamics(year_data)
    categories = build_category_dynamics(year_data)

    # Сохранение таблиц
    general.to_csv(
        TABLES_DIR / "comparison.csv",
        index=False,
        encoding="utf-8-sig"
    )

    words.to_csv(
        TABLES_DIR / "word_dynamics.csv",
        index=False,
        encoding="utf-8-sig"
    )

    categories.to_csv(
        TABLES_DIR / "category_dynamics.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Построение графиков
    plot_total_occurrences(general)
    plot_frequency_per_1000(general)
    plot_comments_percentage(general)
    plot_top_words(words)
    plot_category_share(categories)
    plot_top_categories(categories)

    print("\nАнализ завершён.")
    print(f"Таблицы сохранены в: {TABLES_DIR}")
    print(f"Графики сохранены в: {CHARTS_DIR}")

    print("\nСводная статистика:")
    print(general.to_string(index=False))


if __name__ == "__main__":
    run_comparison()
