"""Glossary and rank introductions, with real examples and common mistakes."""
from dataclasses import dataclass

from .data_bundle import load_bundle


@dataclass(frozen=True, slots=True)
class Topic:
    title: str
    meaning: str
    example: str
    pitfall: str


@dataclass(frozen=True, slots=True)
class Guide:
    title: str
    overview: str
    steps: tuple[str, ...]
    example: str
    advice: str


_data = load_bundle()
TOPICS = {name: Topic(**item) for name, item in _data['topics'].items()}
GUIDES = {
    name: Guide(**{**item, 'steps': tuple(item['steps'])})
    for name, item in _data['guides'].items()
}
