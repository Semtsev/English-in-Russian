import re


def clean_comment_block(block: str) -> str:
    """Удаляет служебную информацию из одного блока комментария."""

    lines = block.strip().splitlines()

    if not lines:
        return ""

    # Удаляем имя пользователя — первая строка блока
    lines = lines[1:]

    cleaned_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Дата и время, например: 12 октября в 14:35
        if re.match(
            r"^\d{1,2}\s+\w+\s+в\s+\d{1,2}:\d{2}$",
            line,
            flags=re.IGNORECASE
        ):
            continue

        # Элементы интерфейса
        if line.lower() in {"ответить", "поделиться", "нравится"}:
            continue

        # Количество лайков
        if re.fullmatch(r"\d+", line):
            continue

        cleaned_lines.append(line)

    return " ".join(cleaned_lines)


def extract_comments(text: str) -> list[str]:
    """Разделяет исходный текст на блоки и очищает каждый блок."""

    blocks = re.split(r"\n\s*\n", text)
    comments = []

    for block in blocks:
        comment = clean_comment_block(block)

        if comment:
            comments.append(comment)

    return comments