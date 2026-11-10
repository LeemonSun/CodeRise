"""Подсказки к обычным ошибкам Python без поиска по интернету."""

import re


EXPLANATIONS = {
    "IndentationError": "Съехал отступ. После строки с двоеточием должен быть блок с отступом, обычно четыре пробела.",
    "TabError": "В одном блоке смешались табуляция и пробелы. Используй четыре пробела на каждый уровень.",
    "SyntaxError": "Python не понял запись. Проверь двоеточие после if/for/def, парные скобки и кавычки.",
    "NameError": "Такого имени сейчас нет. Проверь опечатку и место, где создаётся переменная.",
    "TypeError": "Операция не подходит для этих типов данных. Например, к строке нельзя просто прибавить число.",
    "ValueError": "Значение не подходит для преобразования. Например, int('кот') вызвать нельзя.",
    "ZeroDivisionError": "Делить на ноль нельзя. Проверь число перед знаком деления.",
    "IndexError": "Нужного индекса в списке или строке нет. Первый индекс — 0, последний — len(список) - 1.",
    "KeyError": "В словаре нет такого ключа. Проверь написание или используй get().",
    "EOFError": "Программа запросила больше строк через input(), чем дано в тесте.",
    "RecursionError": "Функция слишком много раз вызвала сама себя. Проверь условие остановки рекурсии.",
    "AttributeError": "У объекта нет такого поля или метода. Посмотри на его тип и проверь название.",
    "FileNotFoundError": "Указанный файл не найден. Учебные задания обычно не требуют открытия внешних файлов.",
    "ImportError": "Не удалось импортировать имя или модуль. Проверь написание и наличие библиотеки.",
    "ModuleNotFoundError": "Такого модуля нет в стандартной библиотеке этой сборки Python.",
}


def explain_python_error(traceback_text: str) -> str:
    """Friendly first line, followed by the actual Python message."""
    error_name = next(
        (name for name in EXPLANATIONS if re.search(r"\b" + re.escape(name) + r":", traceback_text)),
        None,
    )
    if not error_name:
        return "Прочитай последнюю строку сообщения Python: там указана причина ошибки."
    hint = EXPLANATIONS[error_name]
    if error_name == "NameError":
        missing = re.search(r"name '([^']+)' is not defined", traceback_text)
        if missing:
            hint += f"\nНе найдено имя: {missing.group(1)}."
    line_hits = re.findall(r'File "[^"]+", line (\d+)', traceback_text)
    if line_hits:
        hint += f"\nПосмотри строку {line_hits[-1]}."
    return hint
