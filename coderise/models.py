from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Stage:
    code: str
    title: str
    rank: str
    subtitle: str

@dataclass(frozen=True, slots=True)
class Case:
    stdin: str
    expected: str

@dataclass(frozen=True, slots=True)
class Exercise:
    id: str
    stage: str
    title: str
    kind: str
    prompt: str
    starter: str
    tests: tuple[Case, ...] = ()
    answer: str = ""
    hint: str = ""
    explanation: str = ""
    walkthrough: str = ""
    methods: tuple[tuple[str, str], ...] = ()
    concepts: tuple[str, ...] = ()
    difficulty: int = 1
