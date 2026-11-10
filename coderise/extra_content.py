"""Extra exercises and stages G–SSS. Run scripts/export_course.py for editable JSON."""
from .data_bundle import load_bundle
from .models import Case, Exercise, Stage

_data = load_bundle()
MORE_STAGES = tuple(Stage(**stage) for stage in _data['stages'])
EXTRA_EXERCISES = tuple(
    Exercise(
        id=item['id'], stage=item['stage'], title=item['title'],
        kind=item['kind'], prompt=item['prompt'], starter=item['starter'],
        tests=tuple(Case(**case) for case in item['tests']),
        answer=item.get('answer', ''), hint=item.get('hint', ''),
        explanation=item.get('explanation', ''),
        walkthrough=item.get('walkthrough', ''),
        methods=tuple((name, code) for name, code in item.get('methods', ())),
        concepts=tuple(item.get('concepts', ())),
        difficulty=item.get('difficulty', 1),
    )
    for item in _data['exercises']
)
