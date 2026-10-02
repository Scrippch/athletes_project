import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from xml.dom import minidom
from xml.etree import ElementTree as ET

from django.conf import settings

DATA_DIR: Path = Path(settings.MEDIA_ROOT) / 'athletes_data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

SAFE_NAME_RE = re.compile(r'[^A-Za-z0-9_.-]+')
REQUIRED_FIELDS = ('name', 'age', 'sport', 'country')


def sanitize_filename(name: str) -> str:
    name = Path(name).name
    name = SAFE_NAME_RE.sub('_', name)
    return name[:80] or 'file'


def generate_filename(ext: str) -> str:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f'athlete_{ts}_{uuid.uuid4().hex[:8]}.{ext}'


def validate_athlete_dict(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError('Запись должна быть объектом')

    errors = []
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ''):
            errors.append(f'отсутствует поле "{field}"')

    if 'age' in data:
        try:
            age = int(data['age'])
        except (TypeError, ValueError):
            errors.append('поле "age" должно быть числом')
        else:
            if not (10 <= age <= 100):
                errors.append('"age" должен быть в диапазоне 10..100')

    if errors:
        raise ValueError('; '.join(errors))

    return {
        'name': str(data['name']).strip(),
        'age': int(data['age']),
        'sport': str(data['sport']).strip(),
        'country': str(data['country']).strip(),
        'achievements': str(data.get('achievements', '') or '').strip(),
    }


def save_athlete_to_file(athlete: dict, fmt: str) -> str:
    athlete = validate_athlete_dict(athlete)

    if fmt == 'json':
        filename = generate_filename('json')
        path = DATA_DIR / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'athletes': [athlete]}, f, ensure_ascii=False, indent=2)

    elif fmt == 'xml':
        filename = generate_filename('xml')
        path = DATA_DIR / filename
        root = ET.Element('athletes')
        node = ET.SubElement(root, 'athlete')
        for key, value in athlete.items():
            child = ET.SubElement(node, key)
            child.text = str(value)
        raw = ET.tostring(root, encoding='utf-8')
        pretty = minidom.parseString(raw).toprettyxml(indent='  ', encoding='utf-8')
        with open(path, 'wb') as f:
            f.write(pretty)

    else:
        raise ValueError('Неизвестный формат файла')

    return filename


def parse_json_file(path: Path) -> list:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and 'athletes' in data:
        items = data['athletes']
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        raise ValueError('Некорректная структура JSON')

    if not items:
        raise ValueError('Файл не содержит записей')

    return [validate_athlete_dict(x) for x in items]


def parse_xml_file(path: Path) -> list:
    tree = ET.parse(path)
    root = tree.getroot()

    if root.tag == 'athlete':
        items = [root]
    else:
        items = list(root.findall('athlete')) or list(root)

    if not items:
        raise ValueError('Файл не содержит записей')

    result = []
    for el in items:
        d = {child.tag: (child.text or '') for child in el}
        result.append(validate_athlete_dict(d))
    return result


def parse_data_file(path: Path) -> list:
    ext = path.suffix.lower()
    if ext == '.json':
        return parse_json_file(path)
    if ext == '.xml':
        return parse_xml_file(path)
    raise ValueError('Поддерживаются только .json и .xml')


def list_data_files() -> list:
    files = [p for p in DATA_DIR.glob('*') if p.suffix.lower() in ('.json', '.xml')]
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files