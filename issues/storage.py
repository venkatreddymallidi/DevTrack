"""Small JSON-file storage layer, separate from the OOP entities and HTTP views."""
import json
import os
import tempfile
from pathlib import Path
from threading import Lock

from django.conf import settings

# Guards read-check-write sequences inside one Django process. JSON storage is
# for this local exercise; use a database for multi-process production writes.
_WRITE_LOCK = Lock()


def _path(filename):
    if filename not in ('reporters.json', 'issues.json'):
        raise ValueError('Unsupported data file')
    return Path(settings.BASE_DIR) / filename


def read_records(filename):
    path = _path(filename)
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8') as handle:
        records = json.load(handle)
    if not isinstance(records, list):
        raise ValueError(f'{filename} must contain a JSON list')
    return records


def insert_record(filename, record, check_reporter=False):
    """Insert uniquely by ID. For an issue, verify its reporter exists."""
    with _WRITE_LOCK:
        records = read_records(filename)
        if any(item['id'] == record['id'] for item in records):
            raise ValueError('ID already exists')
        if check_reporter:
            reporters = read_records('reporters.json')
            if not any(reporter['id'] == record['reporter_id'] for reporter in reporters):
                raise ValueError('Reporter not found')

        records.append(record)
        path = _path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        # Atomic replacement prevents a partially written JSON file if a write fails.
        temporary_name = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=path.parent,
                prefix=f'.{path.stem}-', suffix='.tmp', delete=False
            ) as handle:
                temporary_name = handle.name
                json.dump(records, handle, ensure_ascii=False, indent=2)
                handle.write('\n')
            os.replace(temporary_name, path)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)
