"""Load the editable lesson bank. Lesson data is JSON; it is never executed."""
import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=1)
def load_bundle() -> dict:
    path = files('coderise').joinpath('data/course_data.json')
    return json.loads(path.read_text(encoding='utf-8'))


@lru_cache(maxsize=1)
def load_legacy() -> dict:
    path = files('coderise').joinpath('data/legacy_data.json')
    return json.loads(path.read_text(encoding='utf-8'))
