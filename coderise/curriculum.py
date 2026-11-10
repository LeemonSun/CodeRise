"""Unified course: 120 exercises, ten ranks, no duplicated identifiers."""
from dataclasses import replace

from .content import EXERCISES as STARTER_EXERCISES, STAGES as STARTER_STAGES
from .data_bundle import load_legacy
from .extra_content import EXTRA_EXERCISES, MORE_STAGES


def enrich(exercise):
    legacy = load_legacy().get(exercise.id)
    if legacy is None:
        return exercise
    walkthrough, options, concepts = legacy
    return replace(
        exercise,
        walkthrough=walkthrough,
        methods=(('По шагам', options[0]), ('Другой вариант', options[1])),
        concepts=tuple(concepts),
    )


STAGES = STARTER_STAGES + MORE_STAGES
EXERCISES = tuple(
    exercise
    for stage in STAGES
    for exercise in (
        tuple(enrich(item) for item in STARTER_EXERCISES if item.stage == stage.code)
        + tuple(item for item in EXTRA_EXERCISES if item.stage == stage.code)
    )
)
EXERCISES_BY_ID = {item.id: item for item in EXERCISES}
STAGES_BY_ID = {item.code: item for item in STAGES}

assert len(EXERCISES) == len(EXERCISES_BY_ID)
assert len(STAGES) == len(STAGES_BY_ID)
