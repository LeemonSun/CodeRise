"""Пояснения к синтаксису строки под курсором. Код не исполняется."""

import io
import tokenize

from .reference import TOPICS

ATTRIBUTE_ONLY = {
    "split", "strip", "get", "lower", "startswith", "count", "pop",
    "sort", "update", "items", "append",
}
CALL_ONLY = {
    "print", "input", "int", "float", "str", "len", "sum", "min",
    "max", "sorted", "enumerate", "map", "list", "dict", "set",
    "range", "all", "any", "divmod",
}


def explain_line(source: str, line_number: int, selected: str = ""):
    """Return source line and tuples (term, glossary entry).

    The tokenizer ignores words inside strings and comments.
    """
    lines = source.splitlines()
    if not 1 <= line_number <= len(lines):
        return "", []
    line = lines[line_number - 1]
    if line.lstrip().startswith("#"):
        return line, [("Комментарий", None)]
    try:
        tokens = [
            token for token in tokenize.generate_tokens(io.StringIO(line + "\n").readline)
            if token.type not in (
                tokenize.ENDMARKER, tokenize.NEWLINE, tokenize.NL,
                tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING,
            )
        ]
    except (tokenize.TokenError, IndentationError):
        return line, []

    found = []
    seen = set()
    for index, token in enumerate(tokens):
        term = token.string
        if token.type in (tokenize.STRING, tokenize.COMMENT) or term not in TOPICS:
            continue
        before = tokens[index - 1].string if index else ""
        after = tokens[index + 1].string if index + 1 < len(tokens) else ""
        if term in ATTRIBUTE_ONLY and before != ".":
            continue
        if term in CALL_ONLY and after != "(":
            continue
        if term not in seen:
            found.append((term, TOPICS[term]))
            seen.add(term)
    if selected in TOPICS and selected not in seen:
        found.insert(0, (selected, TOPICS[selected]))
    return line, found
