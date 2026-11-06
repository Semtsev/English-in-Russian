import re
import pymorphy3


# Создаём морфологический анализатор русского языка
morph = pymorphy3.MorphAnalyzer()


def normalize_word(word: str) -> str:
    """Приводит отдельное русское слово к начальной форме."""

    word = word.lower().replace("ё", "е")

    # Если слово написано кириллицей — лемматизируем
    if re.fullmatch(r"[а-я]+", word):
        parsed = morph.parse(word)[0]
        return parsed.normal_form

    # Английские и смешанные слова пока оставляем без изменений
    return word


def normalize_text(text: str) -> str:
    """Нормализует все слова в комментарии."""

    # Извлекаем слова на русском и английском языках
    words = re.findall(
        r"[a-zA-Z]+(?:[-'][a-zA-Z]+)*|[а-яА-ЯёЁ]+(?:-[а-яА-ЯёЁ]+)*",
        text
    )

    normalized_words = [
        normalize_word(word) for word in words
    ]

    return " ".join(normalized_words)