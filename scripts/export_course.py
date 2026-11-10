"""Export editable course content (JSON) from the built-in lesson pack."""
import json
from pathlib import Path
from coderise.data_bundle import load_bundle


if __name__ == '__main__':
    path = Path('course-editable.json')
    path.write_text(json.dumps(load_bundle(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Created: {path.resolve()}')
